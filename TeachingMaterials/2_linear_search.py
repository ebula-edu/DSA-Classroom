# DSA Lesson 2: Linear Search
# Step-by-step sequential check of elements

def linear_search(arr, target):
    # Traversal loop
    for idx in range(len(arr)):
        print(f"Checking index {idx}: val is {arr[idx]}")
        if arr[idx] == target:
            print(f"Found target {target} at index {idx}!")
            return idx
    print("Target not found in list.")
    return -1

students_list = ["Alice", "Bobby", "Charlie", "Diana"]
target_name = "Charlie"
print(f"Searching for '{target_name}'...")
res = linear_search(students_list, target_name)
