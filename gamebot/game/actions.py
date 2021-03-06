class BaseAction(object):
    name = None
    description = None

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @classmethod
    def __str__(cls):
        return cls.name

    @classmethod
    def command_name(cls):
        return cls.name.lower().replace(" ", "_")

    @staticmethod
    def do_success(game, source_player, target_player):
        pass

    @staticmethod
    def do_failure(game, source_player, target_player):
        pass

    @staticmethod
    def valid_action(source_player, target_player):
        return True
