import time


def completion(query_str, possible):
    if query_str in possible:
        return [query_str]
    else:
        found = []
        for try_str in possible:
            if try_str.startswith(query_str):
                found.append(try_str)
    return found


class EventQueue(object):
    def __init__(self, default_timeout=30):
        self.queue = []
        self.default_timeout = default_timeout

    def add(self, action, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if not action:
            timeout = 0
        time_eff = time.time() + timeout
        self.queue.append((time_eff, action))

