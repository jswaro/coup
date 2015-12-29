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
    def __init__(self, source_player, target_player, action):
        self.source = source_player
        self.target = target_player
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
    def run(game, source):
        game.broadcast_message("{} takes income for 1 coin".format(source))
        responses = []
        game.event_queue.add(Income, responses)

    @staticmethod
    def do_success(game, source, target):
        source.modify_coins_by_action(1)


@action_register(do_action)
class ForeignAid(CoupAction):
    name = "Foreign Aid"
    description = "Take 2 coins"

    @staticmethod
    def run(game, source):
        game.broadcast_message("{} takes foreign aid for 2 coins".format(source))
        responses = [Counter]  # TODO: teammates cannot counter
        game.event_queue.add(ForeignAid, responses)

    @staticmethod
    def do_success(game, source, target):
        source.modify_coins_by_action(2)


@action_register(do_action)
class Tax(CoupAction):
    name = "Tax"
    description = "Take 3 coins"

    @staticmethod
    def run(game, source):
        game.broadcast_message("{} takes tax for 3 coins".format(source))
        responses = [Challenge]
        game.event_queue.add(Tax, responses)

    @staticmethod
    def do_success(game, source, target):
        source.modify_coins_by_action(3)


@action_register(do_action)
class Steal(CoupAction):
    name = "Steal"
    description = "Take 2 coins from another player"

    @staticmethod
    def run(game, source, target):
        if target == source:
            raise GameInvalidOperation("Cannot steal from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(source, target):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        if target.cash() < 1:
            raise GameInvalidOperation("{} has no cash. Choose a different action".format(target))
        cash_to_steal = max(target.cash(), 2)
        game.broadcast_message("{} steals {} coins from {}".format(source, cash_to_steal, target))
        game.add_message_to_queue(target.name(), "Please challenge, counter, or accept with .accept")
        responses = [Challenge, Counter, Accept]
        game.event_queue.add(Steal, responses)

    @staticmethod
    def do_success(game, source, target):
        cash_to_steal = max(target.cash(), 2)
        source.modify_coins_by_action(cash_to_steal)
        target.modify_coins_by_action(-cash_to_steal)


@action_register(do_action)
class Assassinate(CoupAction):
    name = "Assassinate"
    description = "Pay 3 coins, choose player to lose influence"

    @staticmethod
    def run(game, source, target, guess=None):
        if target == source:
            raise GameInvalidOperation("Cannot assassinate from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(source, target):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        source.modify_coins(-3)
        game.broadcast_message("{} assassinates {}".format(source, target))
        if len(target.available_influence) > 1:
            game.add_message_to_queue(target.name(), "Please challenge, counter, or select which card to provide "
                                                     "with .select 1 or .select 2")
            responses = [Challenge, Counter, Select]
        else:
            game.add_message_to_queue(target.name(), "Please challenge, counter, or accept with .accept")
            responses = [Challenge, Counter, Accept]
        game.event_queue.add(Assassinate, responses)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(do_action)
class ExchangeOne(CoupAction):
    name = "Exchange"
    description = "Take 1 cards, return 1 cards to court deck"

    @staticmethod
    def run(game, source):
        game.broadcast_message("{} exchanges influence; draws an influence card".format(source))
        responses = [Challenge]
        game.event_queue.add(ExchangeOne, responses)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(do_action)
class ExchangeTwo(CoupAction):
    name = "Exchange"
    description = "Take 2 cards, return 2 cards to court deck"

    @staticmethod
    def run(game, source):
        game.broadcast_message("{} exchanges influence; draws two influence cards".format(source))
        responses = [Challenge]
        game.event_queue.add(ExchangeTwo, responses)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(do_action)
class Examine(CoupAction):
    name = "Examine"
    description = "Choose player; look at one card, may force Exchange"

    @staticmethod
    def run(game, source, target):
        if target == source:
            raise GameInvalidOperation("Cannot examine from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(source, target):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        game.broadcast_message("{} examines one of {}'s cards".format(source, target))
        if len(target.available_influence) > 1:
            game.add_message_to_queue(target.name(), "Please challenge, counter, or select which card to provide "
                                                     "with .select 1 or .select 2")
            responses = [Challenge, Counter, Select]
        else:
            game.add_message_to_queue(target.name(), "Please challenge, counter, or accept with .accept")
            responses = [Challenge, Counter, Accept]
        game.event_queue.add(Examine, responses)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(do_action)
class Coup(CoupAction):
    name = "Coup"
    description = "Pay 7 coins, choose player to lose influence"

    @staticmethod
    def run(game, source, target, guess=None):
        if target == source:
            raise GameInvalidOperation("Cannot coup from yourself. Choose a different action")
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        if same_team(source, target):
            raise GameInvalidOperation("{} is on your team. Choose a different action".format(target))
        source.modify_coins(-7)
        game.broadcast_message("{} coups {}".format(source, target))
        game.add_message_to_queue(target.name(), "Please challenge, counter, or accept with .accept")
        if len(target.available_influence) > 1:
            game.add_message_to_queue(target.name(), "Please select which card to lose "
                                                     "with .select 1 or .select 2")
            responses = [Select]
        else:
            game.add_message_to_queue(target.name(), "Please challenge, counter, or accept with .accept")
            responses = []
        game.event_queue.add(Coup, responses)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(do_action)
class Convert(CoupAction):
    name = "Convert"
    description = "Change Allegiance.  Place 1 coin yourself or 2 coins for another player on Treasury Reserve"

    @staticmethod
    def run(game, source, target):
        if target.dead():
            raise GameInvalidOperation("{} is dead. Choose a different action".format(target))
        cost = 1
        if target != source:
            cost = 2

        source.modify_coins(-cost)
        game.broadcast_message("{} changes {}'s allegiance".format(source, target))
        responses = []
        game.event_queue.add(Convert, responses)

    @staticmethod
    def do_success(game, source, target):
        target.flip_team()


@action_register(do_action)
class Embezzle(CoupAction):
    name = "Embezzle"
    description = "Take all coins from Treasury Reserve"

    @staticmethod
    def run(game, source):
        coins = game.treasury
        game.broadcast_message("{} takes coins from the treasury.  Gains {} coins.".format(source, coins))
        responses = [Challenge]
        game.event_queue.add(Embezzle, responses)

    @staticmethod
    def do_success(game, source, target):
        source.modify_coin_by_action(game.treasury)
        game.treasury = 0


# Response Actions
@action_register(response_action)
class Counter(CoupAction):
    name = "Counter"
    description = "Use influence to counter an action"

    @staticmethod
    def run(game, source, with_role):
        responses = [Challenge]
        game.event_queue.add(Counter, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(response_action)
class Challenge(CoupAction):
    name = "Challenge"
    description = "Challenge a player's claimed influence"

    @staticmethod
    def run(game, source, target):
        responses = []
        game.event_queue.add(Challenge, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(response_action)
class Accept(CoupAction):
    name = "Accept"
    description = "Accept your fate"

    @staticmethod
    def run(game, source):
        responses = []
        game.event_queue.add(Accept, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(response_action)
class KeepExamine(CoupAction):
    name = "Keep"
    description = "After examine, allows target to keep his card"

    @staticmethod
    def run(game, source):
        responses = []
        game.event_queue.add(KeepExamine, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(response_action)
class ChangeExamine(CoupAction):
    name = "Change"
    description = "After examine, forces target to exchange his card"

    @staticmethod
    def run(game, source):
        responses = []
        game.event_queue.add(ChangeExamine, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(response_action)
class Select(CoupAction):
    name = "Select"
    description = "Makes card selection for game response"

    @staticmethod
    def run(game, source, cards):
        responses = []
        game.event_queue.add(Select, responses, is_response=True)

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


# Miscellaneous game actions
@action_register(game_action)
class Status(CoupAction):
    name = "Status"
    description = "Gets current game status"

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError


@action_register(game_action)
class Forfeit(CoupAction):
    name = "Forfeit"
    description = "Accepts a lose and removes you from the game"

    @staticmethod
    def do_success(game, source, target):
        raise NotImplementedError
