# DSA Lesson 1: Array / Python List CRUD
# Python lists function as dynamic arrays. Let's trace list operations.

# Create (Insert)
students = ["Alice", "Bob"]
print("Initial:", students)

# Insert at index
students.insert(1, "Charlie")
print("After Insert Charlie:", students)

# Append (Insert at end)
students.append("Diana")
print("After Append Diana:", students)

# Read (Indexing / Traversal)
for i in range(len(students)):
    print(f"Index {i}: {students[i]}")

# Update
students[2] = "Bobby"
print("After Update Bob->Bobby:", students)

# Delete
students.pop(1) # Remove Charlie
print("After Pop Charlie:", students)
