def sum_first(n):
    return n * (n + 1) // 2

def sum_recursive(n):
    if n == 1:
        return 1
    return n + sum_recursive(n - 1)

for i in range(1,11):
    assert sum_first(i) == sum_recursive(i), f"Mismatch for n={i}"
    print(f"n={i}: sum_first = {sum_first(i)}, sum_recursive = {sum_recursive(i)}")