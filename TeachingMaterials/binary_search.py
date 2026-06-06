# DSA Demo: Binary Search
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        print(f"Checking index {mid}, value {arr[mid]}")
        
        if arr[mid] == target:
            print("Found target!")
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    print("Target not found.")
    return -1

items = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
print(f"Searching for {target} in {items}")
index = binary_search(items, target)
print(f"Result: target is at index {index}")
