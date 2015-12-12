from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import same_team
from gamebot.game.actions import BaseAction

__author__ = 'jswaro'


class Event(object):
    def __init__(self, target_player, source_player, action):
        self.target = target_player
        self.source = source_player
        self.action = action

    def success(self):
        self.action.do_success(self.target, self.source)

    def failure(self):
        self.action.do_failure(self.target, self.source)


class Income(BaseAction):
    name = "Income"
    description = "Take 1 coin"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(1)

    @staticmethod
    def do_failure(target, source):
        raise GameInvalidOperation('Income cannot be prevented')


class ForeignAid(BaseAction):
    name = "Foreign Aid"
    description = "Take 2 coins"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)


class Tax(BaseAction):
    name = "Tax"
    description = "Take 3 coins"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(3)


class Steal(BaseAction):
    name = "Steal"
    description = "Take 2 coins from another player"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)
        target.modify_coins_by_action(-2)

    @staticmethod
    def valid_action(target, source):
        return not same_team(target, source)


class Assassinate(BaseAction):
    name = "Assassinate"
    description = "Pay 3 coins, choose player to lose influence"

    @staticmethod
    def do_success(target, source):
        source.modify_coins(-3)
        raise NotImplementedError

    @staticmethod
    def do_failure(target, source):
        source.modify_coins(-3)

    @staticmethod
    def valid_action(target, source):
        if target.dead():
            return False
        if target == source:
            return False

        return not same_team(target, source)


class ExchangeOne(BaseAction):
    name = "Exchange"
    description = "Take 1 cards, return 1 cards to court deck"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


class ExchangeTwo(BaseAction):
    name = "Exchange"
    description = "Take 2 cards, return 2 cards to court deck"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


class Examine(BaseAction):
    name = "Examine"
    description = "Choose player; look at one card, may force Exchange"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


class Coup(BaseAction):
    name = "Coup"
    description = "Pay 7 coins, choose player to lose influence"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(-7)
        raise NotImplementedError

    @staticmethod
    def valid_action(target, source):
        return not same_team(target, source)


class Convert(BaseAction):
    name = "Convert"
    description = "Change Allegiance.  Place 1 coin yourself or 2 coins for another player on Treasury Reserve"

    @staticmethod
    def do_success(target, source):
        cost = 1
        if target != source:
            cost = 2

        source.modify_coins_by_action(cost)
        target.flip_team()


class Embezzle(BaseAction):
    name = "Embezzle"
    description = "Take all coins from Treasury Reserve"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError
