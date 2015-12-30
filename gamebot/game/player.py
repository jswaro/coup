from gamebot.game.team import BaseTeam


class BasePlayer(object):
    def __init__(self, name, team=BaseTeam.UNASSIGNED):
        self._name = name
        self._team = team

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name

    @property
    def team(self):
        return self._team

    def set_team(self, team):
        self._team = team
