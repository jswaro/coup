class BaseAction(object):
    name = None
    description = None

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @classmethod
    def __str__(cls):
        return cls.name

    @staticmethod
    def do_success(target, source):
        pass

    @staticmethod
    def do_failure(target, source):
        pass

    @staticmethod
    def valid_action(target, source):
        return True
