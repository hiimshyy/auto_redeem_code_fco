from queue import Queue

class CouponQueue:
    def __init__(self):
        self.q = Queue()

    def push(self, code):
        self.q.put(code)

    def pop(self):
        return self.q.get()

    def is_empty(self):
        return self.q.empty()