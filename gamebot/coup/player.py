from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import Team

__author__ = 'jswaro'


class Player(object):
    def __init__(self, name, team=Team.NONE):
        self.name = name
        self.coins = 2

        self.available_influence = list()
        self.revealed_influence = list()

        self.team = team

    def give_card(self, card):
        self.available_influence.append(card)

    def describe(self):
        return "{0} has {1} coins".format(self.name, self.coins)

    def current_cards(self):
        return [x.short_description() for x in self.available_influence] + \
               [x.short_description() for x in self.revealed_influence]

    def face_up_cards(self):
        return list(self.revealed_influence)

    def influence_remaining(self):
        return len(self.available_influence)

    def kill(self):
        for x in self.available_influence:
            t = self.available_influence.pop()
            self.revealed_influence.append(t)

    def cash(self):
        return self.coins

    def dead(self):
        return len(self.available_influence) == 0

    def modify_cash_by_action(self, amount):
        if amount + self.coins < 0:
            self.coins = 0
        else:
            self.coins += amount

    def modify_cash(self, amount):
        if amount + self.coins < 0:
            raise GameInvalidOperation("You do not have enough coins to perform that action")

        self.coins += amount

    def flip_team(self):
        if self.team == Player.UNASSIGNED:
            return

        if self.team == Player.RED_TEAM:
            self.team = Player.BLUE_TEAM
        else:
            self.team = Player.RED_TEAM

    def get_team(self):
        return self.team
