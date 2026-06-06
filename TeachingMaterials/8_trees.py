# DSA Lesson 8: Binary Search Tree (BST)
# Tree structures with left/right child linkages

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert_bst(root, val):
    if root is None:
        print(f"Creating tree root node: {val}")
        return TreeNode(val)
        
    print(f"Comparing node value {val} with {root.val}")
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root

# Insert nodes
bst_root = None
bst_root = insert_bst(bst_root, 10)
bst_root = insert_bst(bst_root, 5)
bst_root = insert_bst(bst_root, 15)
