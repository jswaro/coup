import random

__author__ = 'jswaro'


class CoupException(Exception):
    pass


class MalformedCLICommand(CoupException):
    pass


class InvalidCLICommand(CoupException):
    pass


class GameNotFoundException(CoupException):
    pass


class GamePermissionError(CoupException):
    pass


class GameInvalidOperation(CoupException):
    pass

valid_player_actions = ["income", "foreign_aid", "coup", "tax", "steal", "assassinate", "exchange"]

'''
There are several different types of events. There are contestable events which occur when a player
makes a decision that can be contested by another player. There are incontestable events that cannot be
contested, only resolved.

Contestable events require resolution from every player, whether it is simply an accept or contest of the statement.

Interrogative events require resolution from only one player and are typically used to resolve a single decision.

Contestable events are limited the originating player, and the contesting player.

Countering events involve all players, but only one player can respond.

Examples:

An interrogative event is a question to a specific player, such as what action they may want to take this turn.

An incontestable event is a statement of fact that cannot be disputed, such as a coup. These actions are resolved
without any input from the other entities.

A contestable event is a statement of fact that can be disputed, such as an attempt of theft by one player against
another. Another player may dispute the fact that the original player had the role necessary to perform the action.
A counter can result in another contestable event, but only contestable in terms of possession rather than counter.

A counter can only be challenged, but a declaration can be countered or challenged. All contestable events fall into
one of three events: CounterEvent, ChallengeEvent, and DeclarationEvent.
'''

class Influence(object):
    def __init__(self, name, action, counteraction):
        self.name = name
        self.action = action
        self.counteraction = counteraction

    def description(self):
        return "Class: {0}\nAction: {1}\nCounter action: {2}\n".format(self.name, self.action, self.counteraction)

    def short_description(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


contessa = Influence("Contessa", "None", "Blocks assassination")
duke = Influence("Duke", "Tax: receive three coins from the treasury", "Blocks foreign aid")
captain = Influence("Captain", "Steal: take two coins from another player", "Blocks stealing")
ambassador = Influence("Ambassador", "Exchange: take two cards from the court deck "
                                     "and exchange with any face down cards you possess", "Blocks stealing")
assassin = Influence("Assassin", "Assassinate: target player loses one influence", "None")


class Game(object):
    def __init__(self, instance, game_creator, name, password, is_expansion=False):
        self.deck = list()
        self.name = name
        self.password = password
        self.game_creator = game_creator

        self.court_deck = list()
        self.treasury = 0

        self.max_players = 6
        if is_expansion:
            self.max_players = 10

        self.expansion_enabled = is_expansion

        self.players = dict()
        self.player_order = list()

        self.current_player = 0

        self.events = list()

        self.stack = list()

        self.messages = list()
        self.messages_to_send = list()

        self.instance = instance

    def add_player(self, player, password):
        if ((password is not None and password != self.password) or
                (password is None and self.password is not None)):
            raise GamePermissionError("Incorrect password. You may not join this game.")
        if player.name in self.players:
            raise GameInvalidOperation("Player {0} is already in the game".format(player.name))

        self.players[player.name] = player

    def populate_deck(self):
        cards = [contessa, duke, captain, assassin]
        if self.expansion_enabled:
            cards.append(ambassador) # FIXME: needs to be inquisitor
        else:
            cards.append(ambassador)

        for c in cards:
            num_cards_each = 3
            if 6 < len(self.players) and len(self.players) <= 8:
                num_cards_each = 4
            elif len(self.players) > 8:
                num_cards_each = 5

            for x in xrange(0, num_cards_each):
                self.deck.append(c)

    def is_creator(self, user):
        return user == self.game_creator

    def start(self):
        if len(self.players) < 2:
            raise GameInvalidOperation("Not enough players to start yet")

        # make a random player the first player
        self.current_player = random.randint(0, len(self.players) - 1)

        # create the deck
        self.populate_deck()

        # shuffle the deck
        random.shuffle(self.deck)

        # deal each player two cards
        for name in self.players:
            current = self.players[name]

            # each player gets two cards
            current.give_card(self.deck.pop())
            current.give_card(self.deck.pop())

        # put the remaining cards into the court deck
        self.court_deck = list(self.deck)

        self.player_order = self.players.keys()

        turn_order = list()
        for x in xrange(0, len(self.players)):
            turn_order.append(self.player_order[(self.current_player + x) % len(self.players)])

        self.broadcast_message("The game has begun. Turn order is {0}.".format(", ".join(turn_order)))

        self.add_message_to_queue(self.current_player_name(), "You are the first player. "
                                                                    "Please choose an action.")

        self.process_outbound_messages()

    def current_player_name(self):
        return self.player_order[self.current_player]

    def long_name(self):
        if self.password is None:
            return self.name

        return "{0} (private)".format(self.name)

    def find_player_by_name(self, name):
        if name not in self.players.keys():
            raise GameInvalidOperation("You are not part of this game.")

        return self.players[name]

    def my_turn(self, user):
        return user == self.player_order[self.current_player]

    def advance_to_next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def progress_to_next_turn(self):
        alive_players = [x for x in self.player_order if not self.players[x].dead()]

        if len(alive_players) == 1:
            for name in self.player_order:
                self.add_message_to_queue(name, "Player {0} has won!".format(alive_players[0]))
        else:
            self.advance_to_next_player()
            while self.players[self.current_player_name()].dead():
                print "{0} is dead... skipping".format(self.current_player_name())
                self.advance_to_next_player()

            self.add_message_to_queue(self.current_player_name(), "It is your turn. Please choose an action.")

    def broadcast_message(self, message, alive_only=False):
        for name in self.player_order:
            if (alive_only and not self.players[name].dead()) or not alive_only:
                self.add_message_to_queue(name, message)
            else:
                print "skipping {0} as they are dead".format(name)

    def add_message_to_queue(self, user, message):
        self.messages_to_send.append((user, message))

    def process_outbound_messages(self):
        while len(self.messages_to_send) > 0:
            user, message = self.messages_to_send.pop(0)

            print "[{0}] {1}".format(user, message)

    def face_up_cards(self):
        face_up = list()
        for name in self.player_order:
            face_up.extend(self.players[name].face_up_cards())

        return ", ".join(face_up)


class Player(object):
    def __init__(self, name):
        self.name = name
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
        for x in self.available_influence:
            t = self.available_influence.pop()
            self.revealed_influence.append(t)

    def cash(self):
        return self.coins

    def dead(self):
        return len(self.available_influence) == 0

    def modify_cash(self, amount):
        if amount + self.coins < 0:
            raise GameInvalidOperation("You do not have enough coins to perform that action")

        self.coins += amount


class Instance(object):
    def __init__(self):
        self.games = dict()

    def add_game(self, name, game):
        if not self.game_exists(name):
            self.games[name] = game
        else:
            raise GameInvalidOperation("A game with this name already exists")

    def game_exists(self, name):
        return name in self.games

    def find_game_by_name(self, name):
        if name not in self.games:
            raise GameNotFoundException("Game '{0}' not found".format(name))

        return self.games[name]

    def find_user_game(self, name):
        for game_name in self.games.keys():
            if name in self.games[game_name].players:
                return self.games[game_name]

        raise GameNotFoundException("User {0} does not appear to be in a game".format(name))


    def print_games(self):
        if len(self.games.keys()) == 0:
            return ""

        games = [self.games[x].long_name() for x in self.games.keys()]
        return "\n".join(games)

def parse_base_create(instance, user, arguments):
    if len(arguments) == 0:
        raise MalformedCLICommand("Not enough arguments")

    name = arguments[0]

    if instance.game_exists(name):
        raise InvalidCLICommand("A game with this name already exists")

    password = None
    if len(arguments) >= 2:
        password = arguments[1]

    game = Game(instance, user, name, password)
    instance.add_game(name, game)

    player = Player(user)
    game.add_player(player, password)

    return "Game '{0}' created".format(name)

def parse_base_start(instance, user, arguments):
    if len(arguments) == 0:
        raise MalformedCLICommand("Not enough arguments")

    name = arguments[0]

    game = instance.find_game_by_name(name)

    if not game.is_creator(user):
        raise GamePermissionError("Only the owner of the game may start the game")

    game.start()

    return "Game '{0}' started".format(name)

def parse_base_join(instance, user, arguments):
    if len(arguments) == 0:
        raise MalformedCLICommand("Not enough arguments")

    game_name = arguments[0]

    password = None

    if len(arguments) >= 2:
        password = arguments[1]

    game = instance.find_game_by_name(game_name)

    player = Player(user)
    game.add_player(player, password)

    return "Joined game '{0}', players: {1}".format(game_name, ", ".join(game.players.keys()))

def parse_base_forfeit(instance, user, arguments):
    return


def parse_base_list(instance, user, arguments):
    return instance.print_games()


def parse_base_help(instance, user, arguments):
    ret = list([
        "Global commands:",
        "  create <name> [password]",
        "  list",
        "  join <name> [password]",
        "  start <name>",
        "  forfeit",
        "",
        "Game commands:",
        "  do income",
        "  do foreign_aid",
        "  do coup <player>",
        "  do tax",
        "  do steal <player>",
        "  do assassinate <player>",
        "  do exchange",
        "  counter <player> with <role>",
        "  challenge <player>",
        "  accept",
        "  status"
    ])

    return "\n".join(ret)

def parse_game_do(instance, game, user, arguments):
    if len(arguments) == 0:
        raise InvalidCLICommand("Not enough arguments")

    if not game.my_turn(user):
        raise GameInvalidOperation("It is not your turn yet.")

    action = arguments[0]

    player = game.find_player_by_name(user)

    if player.cash() >= 10 and action != "coup":
        raise GameInvalidOperation("You have 10 or more coins, you must coup!")

    if action not in valid_player_actions:
        return GameInvalidOperation("You have picked an invalid option. "
                                    "Please choose from {0}.".format(", ".join(valid_player_actions)))

    print "'{0}' is the action".format(action)

    if action == "income":
        player.modify_cash(1)

        game.broadcast_message("{0} took income. {0} has {1} coins.".format(user, player.cash()))

        game.progress_to_next_turn()
    elif action == "foreign_aid":


        pass
    elif action == "coup":
        if len(arguments) < 2:
            raise InvalidCLICommand("You need to specify a target for the coup.")

        target = arguments[1]

        target_player = game.find_player_by_name(target)

        if player.cash() < 7:
            raise GameInvalidOperation("You do not have enough coins to coup. Pick another action.")

        if target_player.dead():
            raise GameInvalidOperation("Your target is already dead. Shame on you. Pick another action.")

        player.modify_cash(-7)
        if target_player.influence_remaining() == 1:
            target_player.kill()

            game.broadcast_message("{0} has lost all their influence. They are out of the game.")
        else:
            # generate decision event
            # TODO: need to add an event for losing influence
            pass

        game.broadcast_message("The list of current face-up cards are '{0}'.".format(game.face_up_cards()))
        game.progress_to_next_turn()
    elif action == "tax":
        # TODO: generate contestable event
        pass
    elif action == "steal":
        # TODO: generate contestable event
        pass
    elif action == "exchange":
        # TODO: generate contestable event
        pass
    elif action == "assassinate":
        # TODO: generate contestable evnet
        pass
    else:
        raise CoupException("Not sure how we got here, but you picked an invalid option")

    game.process_outbound_messages()


def parse_game_challenge(instance, game, user, arguments):
    return

def parse_game_counter(instance, game, user, arguments):
    return

def parse_game_status(instance, game, user, arguments):
    return

class CoupCLIParser(object):
    def __init__(self, instance):
        self.recognized_base_actions = dict(
            create=parse_base_create,
            start=parse_base_start,
            join=parse_base_join,
            forfeit=parse_base_forfeit,
            list=parse_base_list,
            help=parse_base_help)

        self.recognized_game_actions = dict(
            do=parse_game_do,
            challenge=parse_game_challenge,
            counter=parse_game_counter,
            status=parse_game_status)

        self.instance = instance

    def parse_input(self, user, line):
        arguments = line.rstrip().split()

        action = arguments[0]

        ret = ""

        try:
            if action in self.recognized_base_actions:
                ret = self.parse_base_action(user, action, arguments[1:])
            elif action in self.recognized_game_actions:
                ret = self.parse_game_action(user, action, arguments[1:])
        except CoupException as e:
                ret = "Error: {0} ".format(e.message)

        print "[{0}] {1}: {2}".format(user, line.rstrip(), ret)
        return ret

    def parse_base_action(self, user, action, arguments):
        """

        :param user:
        :param action:
        :param arguments:
        """
        return self.recognized_base_actions[action](self.instance, user, arguments)

    def parse_game_action(self, user, action, arguments):
        """

        :param user:
        :param action:
        :param arguments:
        :raise RuntimeWarning:
        """
        game = self.instance.find_user_game(user)

        if game is None:
            raise GameInvalidOperation("{0} is not part of any game".format(user))

        ret = self.recognized_game_actions[action](self.instance, game, user, arguments)

        game.process_outbound_messages()

        return ret


'''
Players may create a game by sending a message to coup-bot in the following syntax:

  create <name> [password]

  * create requests may fail if there is already a game with that name in progress

The game's creator may start the game by issuing the following message to coup-bot:

  start <name>

  * start requests may fail if there are not enough players or there is not a game
    with the provided name

Any player may join a game by sending the following message to coup-bot:

  join <name> [password]

  * join requests may fail if a game with the provided name does not exist, the password
    is incorrect, or the game is already in progress

Any player may leave a game at any point by issuing the following command:

  forfeit

  * quit may fail if the player is not in a game

Any player may request the list of games that are currently available to join with the
  following command:

  list

  * list may fail if the player is already in a game


Once a player is in a game, they may do any of the following commands on their turn, provided they have the necessary
  resources:

  status [player]

  do <action>
    where <action> can be any one of the following:

    - income
    - foreign aid
    - coup
    - tax
    - steal <player>
    - assassinate <player>
    - exchange

    * during an exchange, the player will be prompted for the cards they wish to keep. They will not be able to accept
      more cards than they had prior to the exchange

  * There will be no warning for actions taken that would require a bluff. It is assumed that if you do an illegal
    action, you know that you will lose an influence if someone calls you out on it.

  challenge <player> with <influence>

  * During another player's turn, you may challenge their action. If they have the ability to do the action and reveal
    the card, you will lose an influence.

  counter <player> with <influence>

  * During another player's turn, you may counter their action with an influence of your own. If you bluff
    the influence and are challenged, you will lose an influence accordingly.

A player loses once they have lost all of their influence. At this point, they may leave to join another game.
'''

def unittest():
    instance = Instance()
    parser = CoupCLIParser(instance)

    # there should be no games yet
    assert len(instance.games) == 0
    assert instance.print_games() == ""

    # create jim game
    parser.parse_input('jswaro', 'create jim')
    assert instance.print_games() == "jim"

    # test failure to start
    ret = parser.parse_input('jswaro', 'start jim')
    assert 'Error: Not enough players to start yet' in ret

    # add player
    parser.parse_input('john', 'join jim')
    game = instance.find_game_by_name('jim')
    assert 'jswaro' in game.players.keys() and 'john' in game.players.keys()

    # test not allowed to start
    ret = parser.parse_input('john', 'start jim')
    assert 'Error: Only the owner of the game may start the game' in ret

    # test no game found
    ret = parser.parse_input('jswaro', 'start blargh')
    assert "Error: Game 'blargh' not found" in ret

    # test malformed start
    ret = parser.parse_input('jswaro', 'start')
    assert 'Not enough arguments' in ret

    # test successful start
    ret = parser.parse_input('jswaro', 'start jim')
    assert "Game 'jim' started" in ret

    # test list
    ret = parser.parse_input('jimbob', 'list')
    assert 'jim' == ret

    parser.parse_input('dood', 'create place')
    ret = parser.parse_input('dood', 'list')
    assert 'jim' in ret and 'place' in ret

    parser.parse_input('rawr', 'create roar roarmore')
    ret = parser.parse_input('rawr', 'list')
    assert 'roar (private)' in ret

    ret = parser.parse_input('jim', 'join roar')
    assert 'Error: Incorrect password. You may not join this game' in ret

    ret = parser.parse_input('jim', 'join roar evenmore')
    assert 'Error: Incorrect password. You may not join this game' in ret

    ret = parser.parse_input('jim', 'help')
    assert 'Global commands' in ret

    ret = parser.parse_input('jswaro', 'do income')




def main():
    """
    Main Loop
    """
    instance = Instance()
    parser = CoupCLIParser(instance)




unittest()