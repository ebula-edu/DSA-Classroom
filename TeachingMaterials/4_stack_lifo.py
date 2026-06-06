# DSA Lesson 4: Stack LIFO (Last-In, First-Out)
# Simulating a browser back button history stack

class BrowserHistory:
    def __init__(self):
        self.history_stack = []

    def visit(self, url):
        print(f"Visiting: {url}")
        self.history_stack.append(url) # Push

    def back(self):
        if len(self.history_stack) > 1:
            popped_url = self.history_stack.pop() # Pop
            current_url = self.history_stack[-1]  # Peek
            print(f"Back button pressed. Left {popped_url}. Current page: {current_url}")
            return current_url
        print("Cannot go back. At home page.")
        return None

browser = BrowserHistory()
browser.visit("google.com")
browser.visit("github.com")
browser.visit("wikipedia.org")

browser.back()
browser.back()
