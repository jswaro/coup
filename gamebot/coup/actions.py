from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import same_team
from gamebot.game.actions import BaseAction

__author__ = 'jswaro'

do_action = []
response_action = []
game_action = []


def action_register(action_list):
    def record_entry(cls):
        action_list.append(cls)
        return cls
    return record_entry


class Event(object):
    def __init__(self, target_player, source_player, action):
        self.target = target_player
        self.source = source_player
        self.action = action

    def success(self):
        self.action.do_success(self.target, self.source)

    def failure(self):
        self.action.do_failure(self.target, self.source)


# Do actions - Initial turn actions
@action_register(do_action)
class Income(BaseAction):
    name = "Income"
    description = "Take 1 coin"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(1)

    @staticmethod
    def do_failure(target, source):
        raise GameInvalidOperation('Income cannot be prevented')


@action_register(do_action)
class ForeignAid(BaseAction):
    name = "Foreign Aid"
    description = "Take 2 coins"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)


@action_register(do_action)
class Tax(BaseAction):
    name = "Tax"
    description = "Take 3 coins"

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(3)


@action_register(do_action)
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


@action_register(do_action)
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


@action_register(do_action)
class ExchangeOne(BaseAction):
    name = "Exchange"
    description = "Take 1 cards, return 1 cards to court deck"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class ExchangeTwo(BaseAction):
    name = "Exchange"
    description = "Take 2 cards, return 2 cards to court deck"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Examine(BaseAction):
    name = "Examine"
    description = "Choose player; look at one card, may force Exchange"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
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


@action_register(do_action)
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


@action_register(do_action)
class Embezzle(BaseAction):
    name = "Embezzle"
    description = "Take all coins from Treasury Reserve"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


# Response Actions
@action_register(response_action)
class Counter(BaseAction):
    name = "Counter"
    description = "Use influence to counter an action"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class Challenge(BaseAction):
    name = "Challenge"
    description = "Challenge a player's claimed influence"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class Accept(BaseAction):
    name = "Accept"
    description = "Accept your fate"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class KeepExchange(BaseAction):
    name = "Keep"
    description = "After exchange, signifies which cards to keep"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class KeepExamine(BaseAction):
    name = "Keep"
    description = "After examine, allows target to keep his card"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class ChangeExamine(BaseAction):
    name = "Change"
    description = "After examine, forces target to exchange his card"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


# Miscellaneous game actions
@action_register(game_action)
class Status(BaseAction):
    name = "Status"
    description = "Gets current game status"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(game_action)
class Forfeit(BaseAction):
    name = "Forfeit"
    description = "Accepts a lose and removes you from the game"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError
