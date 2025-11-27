# Sliding Window Cheatsheet

## When to Use Sliding Window?
- **Contiguous** subarray/substring problems
- Keywords: "consecutive", "subarray", "substring", "window"
- Optimize from O(n²) → O(n)

---

## Pattern 1: Fixed-Size Window

### Problem: Maximum/Minimum of K consecutive elements

**Brute Force O(n*k):**
```
FOR each position i:
    sum = 0
    FOR j from i to i+k-1:
        sum += arr[j]
    update result
```

**Optimized O(n):**
```
# Initialize first window
window = sum(arr[0:k])
result = window

# Slide: remove left, add right
FOR i from k to n-1:
    window = window - arr[i-k] + arr[i]
    result = best(result, window)
```

**Example:** arr = [2, 1, 5, 1, 3], k = 3
```
[2,1,5] → 8
[1,5,1] → 8-2+1 = 7
[5,1,3] → 7-1+3 = 9 ✓
```

---

## Pattern 2: Variable-Size Window (Two Pointers)

### Problem: Minimum/Maximum subarray satisfying condition

**Brute Force O(n²):**
```
FOR each start:
    FOR each end:
        check if subarray valid
        update result
```

**Optimized O(n):**
```
left = 0

FOR right from 0 to n-1:
    # EXPAND: include arr[right]
    add arr[right] to window

    # CONTRACT: shrink while invalid/optimal
    WHILE should_shrink:
        remove arr[left] from window
        left++

    update result
```

**Example:** Find min subarray with sum ≥ 7
arr = [2, 3, 1, 2, 4, 3]
```
right=3: sum=8 ≥ 7 → len=4, shrink
right=4: sum=7 ≥ 7 → len=3, shrink
right=5: sum=7 ≥ 7 → len=2 ✓
```

---

## Pattern 3: HashMap + Sliding Window

### Problem: Substring with character constraints

**Template:**
```
char_map = {}  # char → count or last_index
left = 0

FOR right from 0 to n-1:
    # Add s[right] to map
    update char_map[s[right]]

    # Shrink if constraint violated
    WHILE constraint_violated:
        update char_map[s[left]]
        left++

    update result
```

### Variant A: Longest unique substring
```
char_index = {}  # char → last seen index

FOR right from 0 to n-1:
    IF s[right] in char_index AND char_index[s[right]] >= left:
        left = char_index[s[right]] + 1

    char_index[s[right]] = right
    max_len = max(max_len, right - left + 1)
```

### Variant B: At most K distinct characters
```
char_count = {}  # char → count

FOR right from 0 to n-1:
    char_count[s[right]]++

    WHILE len(char_count) > k:
        char_count[s[left]]--
        IF char_count[s[left]] == 0:
            delete char_count[s[left]]
        left++

    max_len = max(max_len, right - left + 1)
```

---

## Pattern 4: Monotonic Deque

### Problem: Maximum/Minimum in each window of size k

**Brute Force O(n*k):**
```
FOR each window:
    result.append(max(window))
```

**Optimized O(n):**
```
deque = []  # stores INDICES

FOR i from 0 to n-1:
    # Remove expired indices
    WHILE deque and deque[0] <= i - k:
        deque.popleft()

    # Remove smaller elements (for max)
    WHILE deque and arr[deque[-1]] < arr[i]:
        deque.pop()

    deque.append(i)

    # Record result when window complete
    IF i >= k - 1:
        result.append(arr[deque[0]])
```

**Key Insight:** Smaller elements will never be max if larger element is in window

---

## Quick Reference Table

| Problem | Type | Data Structure | Time |
|---------|------|----------------|------|
| Max sum of k elements | Fixed | None | O(n) |
| Min subarray ≥ target | Variable | None | O(n) |
| Longest unique substring | Variable | HashMap | O(n) |
| At most k distinct | Variable | HashMap | O(n) |
| Sliding window max | Fixed | Deque | O(n) |
| Min window substring | Variable | HashMap | O(n) |

---

## Common Mistakes

1. **Off-by-one errors**
   - Window [i, i+k-1] has k elements
   - Length = right - left + 1

2. **Not checking HashMap bounds**
   ```python
   # Wrong
   if char in map and map[char] >= left

   # This is correct - check both conditions
   ```

3. **Forgetting to update HashMap**
   - Always update after shrinking window

4. **Wrong shrink condition**
   - `while` not `if` - may need multiple shrinks

---

## Interview Tips

1. **Start with brute force** - show you understand the problem
2. **Identify the pattern** - fixed or variable window?
3. **Write the template** - then fill in the details
4. **Trace through example** - verify logic before coding
5. **Time/Space complexity** - always mention O(n) optimization

---

## Practice Problems by Difficulty

### Easy
- Maximum Sum Subarray of Size K
- First Negative in Every Window of Size K

### Medium
- Longest Substring Without Repeating (LC #3)
- Minimum Size Subarray Sum (LC #209)
- Fruit Into Baskets (LC #904)
- Longest Repeating Character Replacement (LC #424)

### Hard
- Sliding Window Maximum (LC #239)
- Minimum Window Substring (LC #76)
- Substring with Concatenation of All Words (LC #30)

---

## Code Templates (Copy-Paste Ready)

### Fixed Window Sum
```python
def fixed_window(arr, k):
    window = sum(arr[:k])
    result = window

    for i in range(k, len(arr)):
        window = window - arr[i-k] + arr[i]
        result = max(result, window)

    return result
```

### Variable Window (Minimum)
```python
def variable_window_min(arr, target):
    left = 0
    window_sum = 0
    min_len = float('inf')

    for right in range(len(arr)):
        window_sum += arr[right]

        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= arr[left]
            left += 1

    return min_len if min_len != float('inf') else 0
```

### Variable Window (Maximum)
```python
def variable_window_max(arr, condition):
    left = 0
    max_len = 0

    for right in range(len(arr)):
        # expand

        while not valid():
            # shrink
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len
```

### Longest Unique Substring
```python
def longest_unique(s):
    char_index = {}
    left = 0
    max_len = 0

    for right in range(len(s)):
        if s[right] in char_index and char_index[s[right]] >= left:
            left = char_index[s[right]] + 1

        char_index[s[right]] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

### Sliding Window Maximum
```python
from collections import deque

def sliding_max(arr, k):
    dq = deque()
    result = []

    for i in range(len(arr)):
        while dq and dq[0] <= i - k:
            dq.popleft()

        while dq and arr[dq[-1]] < arr[i]:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(arr[dq[0]])

    return result
```
