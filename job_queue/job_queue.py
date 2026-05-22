import queue
class JobQueue:
    def __init__(self):
        self.q = queue.Queue()

    def load(self, messages):
        for message in messages:
            self.q.put(message)
        print(f"queue loaded {self.q.qsize()}jobs")
    def next_job(self):
        if not self.q.empty():
            return self.q.get()
        return None
    
    def is_empty(self):
        return self.q.empty()
