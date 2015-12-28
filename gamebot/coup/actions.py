from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import same_team
from gamebot.game.actions import BaseAction
from gamebot.coup.events import event_queue

__author__ = 'jswaro'

do_action = []
response_action = []
game_action = []


def action_register(action_list):
    def record_entry(cls):
        action_list.append(cls)
        return cls
    return record_entry


class CoupAction(BaseAction):
    @staticmethod
    def announce():
        return "No announcement implemented"


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
class Income(CoupAction):
    name = "Income"
    description = "Take 1 coin"

    @staticmethod
    def run(game, target, source):
        game.broadcast_message("{} takes an income of 1 coin".format(source))

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(1)

    @staticmethod
    def do_failure(target, source):
        raise GameInvalidOperation('Income cannot be prevented')


@action_register(do_action)
class ForeignAid(CoupAction):
    name = "Foreign Aid"
    description = "Take 2 coins"

    @staticmethod
    def announce(target, source):
        return "{} takes an foreign aid of 2 coins".format(source)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)


@action_register(do_action)
class Tax(CoupAction):
    name = "Tax"
    description = "Take 3 coins"

    @staticmethod
    def announce(target, source):
        return "{} takes an tax of 3 coins".format(source)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(3)


@action_register(do_action)
class Steal(CoupAction):
    name = "Steal"
    description = "Take 2 coins from another player"

    @staticmethod
    def announce(target, source):
        return "{} steals 2 coins from {}".format(source, target)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)
        target.modify_coins_by_action(-2)

    @staticmethod
    def valid_action(target, source):
        return not same_team(target, source)


@action_register(do_action)
class Assassinate(CoupAction):
    name = "Assassinate"
    description = "Pay 3 coins, choose player to lose influence"

    @staticmethod
    def announce(target, source):
        # TODO no need to select if only 1 left
        return "{} assassinates {}. {}, please select an influence to lose (example: select 1)".format(source, target, target)

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
class ExchangeOne(CoupAction):
    name = "Exchange"
    description = "Take 1 cards, return 1 cards to court deck"

    @staticmethod
    def announce(target, source):
        return "{} draws an influence card.  Must return 1 to the deck.".format(source)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class ExchangeTwo(CoupAction):
    name = "Exchange"
    description = "Take 2 cards, return 2 cards to court deck"

    @staticmethod
    def announce(target, source):
        return "{} draws two influence card.  Must return two to the deck.".format(source)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Examine(CoupAction):
    name = "Examine"
    description = "Choose player; look at one card, may force Exchange"

    @staticmethod
    def announce(target, source):
        return "{} examines one of {}'s cards.  {}, please select a card (example: select 1).".format(source, target, target)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Coup(CoupAction):
    name = "Coup"
    description = "Pay 7 coins, choose player to lose influence"

    @staticmethod
    def announce(target, source):
        # TODO no need to select if only 1 left
        return "{} coups {}. {}, please select an influence to lose (example: select 1)".format(source, target, target)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(-7)
        raise NotImplementedError

    @staticmethod
    def valid_action(target, source):
        return not same_team(target, source)


@action_register(do_action)
class Convert(CoupAction):
    name = "Convert"
    description = "Change Allegiance.  Place 1 coin yourself or 2 coins for another player on Treasury Reserve"

    @staticmethod
    def announce(target, source):
        # TODO no need to select if only 1 left
        return "{} changes {}'s allegiance".format(source, target)

    @staticmethod
    def do_success(target, source):
        cost = 1
        if target != source:
            cost = 2

        source.modify_coins_by_action(cost)
        target.flip_team()


@action_register(do_action)
class Embezzle(CoupAction):
    name = "Embezzle"
    description = "Take all coins from Treasury Reserve"

    @staticmethod
    def announce(target, source):
        # TODO no need to select if only 1 left
        return "{} takes all coins from the treasury".format(source)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


# Response Actions
@action_register(response_action)
class Counter(CoupAction):
    name = "Counter"
    description = "Use influence to counter an action"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class Challenge(CoupAction):
    name = "Challenge"
    description = "Challenge a player's claimed influence"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class Accept(CoupAction):
    name = "Accept"
    description = "Accept your fate"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class KeepExamine(CoupAction):
    name = "Keep"
    description = "After examine, allows target to keep his card"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class ChangeExamine(CoupAction):
    name = "Change"
    description = "After examine, forces target to exchange his card"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(response_action)
class Select(CoupAction):
    name = "Select"
    description = "Makes card selection for game response"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


# Miscellaneous game actions
@action_register(game_action)
class Status(CoupAction):
    name = "Status"
    description = "Gets current game status"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(game_action)
class Forfeit(CoupAction):
    name = "Forfeit"
    description = "Accepts a lose and removes you from the game"

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError
