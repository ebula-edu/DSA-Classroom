# DSA Lesson 6: Singly Linked List
# Custom nodes containing value and next pointers

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def insert_at_beginning(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        print(f"Inserted head: {data}")

    def traverse(self):
        curr = self.head
        while curr:
            print(f"Traversing node: {curr.val}")
            curr = curr.next

# Create SLL
sll = SinglyLinkedList()
sll.insert_at_beginning("C")
sll.insert_at_beginning("B")
sll.insert_at_beginning("A")

sll.traverse()
