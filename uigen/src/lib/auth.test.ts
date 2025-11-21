import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Use vi.hoisted to create mocks that can be referenced in vi.mock
const { mockSign, mockCookieStore, mockSignJWTInstance, mockJwtVerify } = vi.hoisted(() => {
  const instance = {
    setProtectedHeader: vi.fn().mockReturnThis(),
    setExpirationTime: vi.fn().mockReturnThis(),
    setIssuedAt: vi.fn().mockReturnThis(),
    sign: vi.fn().mockResolvedValue("mock-token"),
  };
  return {
    mockSign: instance.sign,
    mockSignJWTInstance: instance,
    mockCookieStore: {
      get: vi.fn(),
      set: vi.fn(),
      delete: vi.fn(),
    },
    mockJwtVerify: vi.fn(),
  };
});

// Mock server-only
vi.mock("server-only", () => ({}));

// Mock jose
vi.mock("jose", () => ({
  SignJWT: vi.fn().mockImplementation(() => mockSignJWTInstance),
  jwtVerify: mockJwtVerify,
}));

// Mock next/headers cookies
vi.mock("next/headers", () => ({
  cookies: vi.fn().mockResolvedValue(mockCookieStore),
}));

import { createSession, getSession } from "./auth";
import { SignJWT } from "jose";

describe("createSession", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should create a session with JWT token and set cookie", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSign).toHaveBeenCalled();
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "auth-token",
      "mock-token",
      expect.objectContaining({
        httpOnly: true,
        sameSite: "lax",
        path: "/",
      })
    );
  });

  it("should set cookie expiration to 7 days", async () => {
    const now = Date.now();
    vi.setSystemTime(now);

    await createSession("user-123", "test@example.com");

    const setCookieCall = mockCookieStore.set.mock.calls[0];
    const cookieOptions = setCookieCall[2];
    const expectedExpiry = new Date(now + 7 * 24 * 60 * 60 * 1000);

    expect(cookieOptions.expires.getTime()).toBe(expectedExpiry.getTime());
  });

  it("should create SignJWT with correct session payload", async () => {
    const now = Date.now();
    vi.setSystemTime(now);

    await createSession("user-456", "user@test.com");

    expect(SignJWT).toHaveBeenCalledWith(
      expect.objectContaining({
        userId: "user-456",
        email: "user@test.com",
        expiresAt: new Date(now + 7 * 24 * 60 * 60 * 1000),
      })
    );
  });

  it("should set HS256 algorithm in protected header", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWTInstance.setProtectedHeader).toHaveBeenCalledWith({
      alg: "HS256",
    });
  });

  it("should set JWT expiration time to 7 days", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWTInstance.setExpirationTime).toHaveBeenCalledWith("7d");
  });

  it("should call setIssuedAt for JWT", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWTInstance.setIssuedAt).toHaveBeenCalled();
  });

  it("should set secure flag to false in development", async () => {
    const originalEnv = process.env.NODE_ENV;
    vi.stubEnv("NODE_ENV", "development");

    await createSession("user-123", "test@example.com");

    const setCookieCall = mockCookieStore.set.mock.calls[0];
    const cookieOptions = setCookieCall[2];

    expect(cookieOptions.secure).toBe(false);

    vi.stubEnv("NODE_ENV", originalEnv ?? "test");
  });

  it("should set secure flag to true in production", async () => {
    const originalEnv = process.env.NODE_ENV;
    vi.stubEnv("NODE_ENV", "production");

    await createSession("user-123", "test@example.com");

    const setCookieCall = mockCookieStore.set.mock.calls[0];
    const cookieOptions = setCookieCall[2];

    expect(cookieOptions.secure).toBe(true);

    vi.stubEnv("NODE_ENV", originalEnv ?? "test");
  });

  it("should use correct cookie name", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "auth-token",
      expect.any(String),
      expect.any(Object)
    );
  });

  it("should handle different user IDs and emails", async () => {
    await createSession("different-user-id", "different@email.com");

    expect(SignJWT).toHaveBeenCalledWith(
      expect.objectContaining({
        userId: "different-user-id",
        email: "different@email.com",
      })
    );
  });
});

describe("getSession", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return null when no token cookie exists", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const result = await getSession();

    expect(result).toBeNull();
    expect(mockCookieStore.get).toHaveBeenCalledWith("auth-token");
  });

  it("should return null when cookie value is undefined", async () => {
    mockCookieStore.get.mockReturnValue({ value: undefined });

    const result = await getSession();

    expect(result).toBeNull();
  });

  it("should return session payload when token is valid", async () => {
    const mockPayload = {
      userId: "user-123",
      email: "test@example.com",
      expiresAt: new Date(),
    };
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    mockJwtVerify.mockResolvedValue({ payload: mockPayload });

    const result = await getSession();

    expect(result).toEqual(mockPayload);
    expect(mockJwtVerify).toHaveBeenCalled();
    expect(mockJwtVerify.mock.calls[0][0]).toBe("valid-token");
  });

  it("should return null when JWT verification fails", async () => {
    mockCookieStore.get.mockReturnValue({ value: "invalid-token" });
    mockJwtVerify.mockRejectedValue(new Error("Invalid token"));

    const result = await getSession();

    expect(result).toBeNull();
  });

  it("should return null when token is expired", async () => {
    mockCookieStore.get.mockReturnValue({ value: "expired-token" });
    mockJwtVerify.mockRejectedValue(new Error("Token expired"));

    const result = await getSession();

    expect(result).toBeNull();
  });

  it("should call jwtVerify with the token from cookie", async () => {
    const testToken = "test-jwt-token-123";
    mockCookieStore.get.mockReturnValue({ value: testToken });
    mockJwtVerify.mockResolvedValue({
      payload: { userId: "user-1", email: "a@b.com", expiresAt: new Date() },
    });

    await getSession();

    expect(mockJwtVerify).toHaveBeenCalled();
    expect(mockJwtVerify.mock.calls[0][0]).toBe(testToken);
  });
});
