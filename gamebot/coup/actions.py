from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.team import same_team
from gamebot.game.actions import BaseAction


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

    def run(self, game, target, source):
        game.broadcast_message("{} takes income for 1 coin".format(source))
        responses = []
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(1)


@action_register(do_action)
class ForeignAid(CoupAction):
    name = "Foreign Aid"
    description = "Take 2 coins"

    def run(self, game, target, source):
        game.broadcast_message("{} takes foreign aid for 2 coins".format(source))
        responses = [Counter]  # TODO: teammates cannot counter
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(2)


@action_register(do_action)
class Tax(CoupAction):
    name = "Tax"
    description = "Take 3 coins"

    def run(self, game, target, source):
        game.broadcast_message("{} takes tax for 3 coins".format(source))
        responses = [Challenge]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        source.modify_coins_by_action(3)


@action_register(do_action)
class Steal(CoupAction):
    name = "Steal"
    description = "Take 2 coins from another player"

    def run(self, game, target, source):
        if target == source:
            raise GameInvalidOperation("Cannot steal from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(target, source):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        if target.cash() < 1:
            raise GameInvalidOperation("{} has no cash. Choose a different action".format(target))
        cash_to_steal = max(target.cash(), 2)
        game.broadcast_message("{} steals {} coins from {}".format(source, cash_to_steal, target))
        responses = [Challenge, Counter, Accept]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        cash_to_steal = max(target.cash(), 2)
        source.modify_coins_by_action(cash_to_steal)
        target.modify_coins_by_action(-cash_to_steal)


@action_register(do_action)
class Assassinate(CoupAction):
    name = "Assassinate"
    description = "Pay 3 coins, choose player to lose influence"

    def run(self, game, target, source):
        if target == source:
            raise GameInvalidOperation("Cannot assassinate from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(target, source):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        source.modify_coins(-3)
        game.broadcast_message("{} assassinates {}".format(source, target))
        responses = [Challenge, Counter, Select, Accept]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class ExchangeOne(CoupAction):
    name = "Exchange"
    description = "Take 1 cards, return 1 cards to court deck"

    def run(self, game, target, source):
        game.broadcast_message("{} exchanges influence; draws an influence card".format(source))
        responses = [Challenge]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class ExchangeTwo(CoupAction):
    name = "Exchange"
    description = "Take 2 cards, return 2 cards to court deck"

    def run(self, game, target, source):
        game.broadcast_message("{} exchanges influence; draws two influence cards".format(source))
        responses = [Challenge]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Examine(CoupAction):
    name = "Examine"
    description = "Choose player; look at one card, may force Exchange"

    def run(self, game, target, source):
        if target == source:
            raise GameInvalidOperation("Cannot examine from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(target, source):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        game.broadcast_message("{} examines one of {}'s cards".format(source, target))
        responses = [Challenge, Counter, Select, Accept]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Coup(CoupAction):
    name = "Coup"
    description = "Pay 7 coins, choose player to lose influence"

    def run(self, game, target, source):
        if target == source:
            raise GameInvalidOperation("Cannot coup from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(target, source):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        source.modify_coins(-7)
        game.broadcast_message("{} coups {}".format(source, target))
        responses = []
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        raise NotImplementedError


@action_register(do_action)
class Convert(CoupAction):
    name = "Convert"
    description = "Change Allegiance.  Place 1 coin yourself or 2 coins for another player on Treasury Reserve"

    def run(self, game, target, source):
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        cost = 1
        if target != source:
            cost = 2

        source.modify_coins(-cost)
        game.broadcast_message("{} changes {}'s allegiance".format(source, target))
        responses = []
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(target, source):
        target.flip_team()


@action_register(do_action)
class Embezzle(CoupAction):
    name = "Embezzle"
    description = "Take all coins from Treasury Reserve"

    def run(self, game, target, source):
        coins = game.treasury
        game.broadcast_message("{} takes coins from the treasury.  Gains {} coins.".format(source, coins))
        responses = [Challenge]
        game.eventqueue.add(self, responses)

    @staticmethod
    def do_success(game, target, source):
        source.modify_coin_by_action(game.treasury)
        game.treasury = 0


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
