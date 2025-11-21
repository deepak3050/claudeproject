# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UIGen is an AI-powered React component generator with live preview. It uses Claude AI to generate React components that are displayed in real-time within a virtual file system (no files written to disk).

## Tech Stack


- **Framework**: Next.js 15 with App Router, React 19, TypeScript
- **Styling**: Tailwind CSS v4
- **Database**: Prisma with SQLite
- **AI**: Anthropic Claude AI via Vercel AI SDK (@ai-sdk/anthropic)
- **Testing**: Vitest with React Testing Library
- **Key Libraries**: Monaco Editor, Babel Standalone, React Markdown

## Development Commands

### Setup
```bash
npm run setup  # Install dependencies + generate Prisma client + run migrations
```

### Development
```bash
npm run dev              # Start dev server with Turbopack
npm run dev:daemon       # Start dev server in background, logs to logs.txt
```

### Testing
```bash
npm test                 # Run tests with Vitest
```

### Build & Production
```bash
npm run build            # Build for production
npm start                # Start production server
npm run lint             # Run ESLint
```

### Database
```bash
npx prisma generate      # Generate Prisma client
npx prisma migrate dev   # Run migrations
npm run db:reset         # Reset database (force)
```

## Architecture

### Core Systems

#### 1. Virtual File System (`src/lib/file-system.ts`)
- **VirtualFileSystem class**: In-memory file system using Map-based tree structure
- Files stored as `FileNode` objects (type: "file" | "directory")
- Key methods: `createFile()`, `updateFile()`, `deleteFile()`, `rename()`, `serialize()`, `deserialize()`
- Supports text editor commands: `viewFile()`, `replaceInFile()`, `insertInFile()`
- No files are written to disk; everything exists in memory

#### 2. AI Chat Integration (`src/app/api/chat/route.ts`)
- Endpoint: POST `/api/chat`
- Uses Vercel AI SDK's `streamText()` with Claude model
- Two AI tools provided to the model:
  - `str_replace_editor`: Edit files via string replacement (`src/lib/tools/str-replace.ts`)
  - `file_manager`: Rename/delete files (`src/lib/tools/file-manager.ts`)
- System prompt from `src/lib/prompts/generation.tsx` (uses prompt caching)
- Auto-saves project state to database on completion (if authenticated)
- Max 40 steps for real AI, 4 steps for mock provider (no API key)

#### 3. JSX Transformation (`src/lib/transform/jsx-transformer.ts`)
- **transformJSX()**: Transforms JSX/TSX to JavaScript using Babel Standalone
- **createImportMap()**: Generates import map with blob URLs for browser execution
- Handles CSS imports separately, collects styles
- Third-party packages resolved via `https://esm.sh/`
- Supports `@/` alias (maps to root directory)
- Creates placeholder modules for missing imports
- Returns transform errors separately for display

#### 4. Authentication (`src/lib/auth.ts`)
- JWT-based sessions using `jose` library
- Session duration: 7 days
- Cookie name: `auth-token`
- Functions: `createSession()`, `getSession()`, `deleteSession()`, `verifySession()`
- Password hashing via `bcrypt`
- Environment variable: `JWT_SECRET` (defaults to "development-secret-key")

#### 5. Database Schema (`prisma/schema.prisma`)
- **User**: id, email (unique), password, createdAt, updatedAt
- **Project**: id, name, userId (nullable), messages (JSON string), data (JSON string), createdAt, updatedAt
- Projects can be anonymous (userId = null) or owned by a user
- Prisma client generated to `src/generated/prisma/`

### Key Contexts

- **FileSystemContext** (`src/lib/contexts/file-system-context.tsx`): Manages virtual file system state
- **ChatContext** (`src/lib/contexts/chat-context.tsx`): Manages chat messages and AI interactions

### Component Structure

- **Chat**: `src/components/chat/` - ChatInterface, MessageList, MessageInput, MarkdownRenderer
- **Editor**: `src/components/editor/` - CodeEditor (Monaco), FileTree
- **Preview**: `src/components/preview/` - PreviewFrame (renders generated components in iframe)
- **Auth**: `src/components/auth/` - SignInForm, SignUpForm, AuthDialog
- **UI**: `src/components/ui/` - Shadcn-style components (button, dialog, tabs, etc.)

### Routes

- `/` - Main page with chat/editor/preview interface
- `/[projectId]/page` - Load existing project by ID
- `/api/chat` - AI chat endpoint

## Important Notes

### Environment Variables
- **ANTHROPIC_API_KEY**: Optional. Without it, mock responses are returned instead of real AI generation
- **JWT_SECRET**: Used for session management (defaults to "development-secret-key")
- **DATABASE_URL**: Configured in `prisma/schema.prisma` (file:./dev.db)

### Testing Strategy
- Tests located in `__tests__/` directories next to components
- Test files use `.test.tsx` or `.test.ts` extension
- Vitest configured with jsdom environment
- Path aliases (`@/`) work in tests via `vite-tsconfig-paths`

### Code Generation Flow
1. User sends message via ChatInterface
2. Message posted to `/api/chat` with current file system state
3. AI model receives system prompt and two tools (str_replace_editor, file_manager)
4. Model generates/edits files using tools
5. File system updates trigger preview refresh
6. Preview transforms JSX → JS, creates import map, renders in iframe
7. On completion, project saved to database (authenticated users only)

### Anonymous Users
- Anonymous users tracked via `src/lib/anon-work-tracker.ts`
- Projects can be created without authentication (userId = null)
- Limited functionality compared to authenticated users

### Preview System
- Entry point: `/App.tsx` by default
- Tailwind CSS loaded via CDN in preview iframe
- React/React-DOM loaded from `esm.sh`
- Error boundary catches runtime errors
- Syntax errors displayed with formatted error UI
- CSS files collected and injected as `<style>` tags
