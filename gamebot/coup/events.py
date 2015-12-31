import time

from gamebot.coup.exceptions import GameInvalidOperation


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
    def __init__(self, game, default_timeout=30):
        self.game = game
        self.queue = []
        self.default_timeout = default_timeout
        self.next_event = None

    def add(self, action, responses, source, target=None, timeout=None, is_response=False):
        if self.queue and not is_response:
            raise GameInvalidOperation("Primary action already done this turn")
        if not self.queue and is_response:
            raise GameInvalidOperation("Primary action not yet done this turn")

        if not is_response:
            if timeout is None:
                timeout = self.default_timeout
            if not responses:
                timeout = 0
            self.next_event = time.time() + timeout
            self.queue.append((action, source, target))
        else:
            pass

    def check(self):
        if self.next_event is not None and time.time() >= self.next_event:
            self.resolve("Default")

    def resolve(self, type, **kargs):
        action, source, target = self.queue.pop()
        if type == "Fail":
            results = action.do_failure(self.game, source, target)
        elif type == "Success":
            results = action.do_success(self.game, source, target)
        else:
            results = action.do_default(self.game, source, target)

        if results is not None:
            self.resolve(results)


