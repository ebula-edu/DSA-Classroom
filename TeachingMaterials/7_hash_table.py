# DSA Lesson 7: Hash Tables (Python Dictionaries)
# Key-Value pairs with average lookup time O(1)

# Simulating a classroom gradebook
gradebook = {}

# Insert/Update (Hash mapping)
gradebook["Alice"] = 92
gradebook["Bob"] = 85
gradebook["Charlie"] = 78
print("Gradebook:", gradebook)

# Read lookup
search_name = "Bob"
if search_name in gradebook:
    score = gradebook[search_name]
    print(f"Found Bob's score: {score}")

# Delete
del gradebook["Charlie"]
print("After Deletion:", gradebook)
