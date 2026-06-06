# DSA Lesson 3: Binary Search
# O(log N) Search on sorted arrays

def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        print(f"Checking index {mid}: val is {arr[mid]}")
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
target_num = 23
print(f"Sorted array: {numbers}")
res = binary_search(numbers, target_num)
print(f"Result: target is at index {res}")
