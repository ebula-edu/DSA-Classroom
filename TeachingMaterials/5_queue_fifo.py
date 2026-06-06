# DSA Lesson 5: Queue FIFO (First-In, First-Out)
# Simulating a printer queue using collections.deque

from collections import deque

class PrinterQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue_job(self, doc_name):
        print(f"Enqueuing print job: {doc_name}")
        self.queue.append(doc_name)

    def dequeue_job(self):
        if self.queue:
            job = self.queue.popleft() # O(1) front deletion
            print(f"Printing: {job}")
            return job
            
        print("No jobs in queue.")
        return None

printer = PrinterQueue()
printer.enqueue_job("Syllabus.pdf")
printer.enqueue_job("LectureNotes.docx")
printer.enqueue_job("Homework_1.pdf")

printer.dequeue_job()
printer.dequeue_job()
