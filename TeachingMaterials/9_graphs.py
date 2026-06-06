# DSA Lesson 9: Graphs
# Adjacency list representation with traversal

# Adjacency List dictionary
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": []
}

print("Adjacency List Graph:", graph)

# Walk vertices
for vertex in graph:
    neighbors = graph[vertex]
    print(f"Vertex {vertex} connects to neighbors: {neighbors}")
