from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import Team
from gamebot.game.player import BasePlayer


class Player(BasePlayer):
    def __init__(self, name, team=Team.UNASSIGNED):
        super().__init__(name, team)

        self.coins = 2

        self.available_influence = list()
        self.revealed_influence = list()

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
        while self.available_influence:
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
        if self.team == Team.UNASSIGNED:
            raise GameInvalidOperation("System Error: No team assigned")

        if self.team == Team.REFORMIST:
            self.team = Team.LOYALIST
        elif self.team == Team.LOYALIST:
            self.team = Team.REFORMIST
        else:
            raise GameInvalidOperation("System Error: Unknown team assigned")
