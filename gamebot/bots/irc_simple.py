from __future__ import print_function

import logging
import re
import socket
import ssl
import time
from collections import deque


class irc_connection():
    def __init__(self, parser, channellist, botnick, botpass=None, server='chat.freenode.net', usessl=True, port=None):
        print(parser, channellist, botnick, botpass, server, usessl, port)

        # First time running the bot considering using register = True to take care of some irc setup automatically
        register = False
        email = ""

        if port is None:
            if usessl:
                port = 6697
            else:
                port = 6667
        self.server = server
        self.port = port
        self.botnick = botnick
        self.parser = parser
        self.msgqueue = deque()
        self.lastsent = 0
        self.prevdelay = None
        if usessl:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsocket = ssl.wrap_socket(raw_socket)
            print((server, port))
            self.ircsocket.connect((server, port))
        else:
            self.ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsocket.connect((server, port))
        self.ircsocket.setblocking(False)
        if register:
            self.sendmsg("nickserv", "register {} {}".format(botpass, email))
            self.sendmsg("nickserv", "set enforce on")
        self.identify(botnick, botpass)
        self.game_rooms = deque()
        for channel in channellist:
            if channel[0] != '#':
                raise SyntaxError("Channel names must start with #")
            self.joinchan(channel)
        for game_number in range(1, 11):
            # Non-primary rooms start with ##, as specified by irc standards
            game_room_name = "#{}_gameroom_{}".format(channellist[0], game_number)
            self.game_rooms.append(game_room_name)
            self.joinchan(game_room_name)
            if register:
                self.sendmsg("chanserv", "register {}".format(game_room_name), delay=1)
                self.sendmsg("chanserv", "FLAGS {} {} +O".format(game_room_name, botnick), delay=1)
                self.modes(game_room_name, "+r")
        self.assigned_game_rooms = {}

    def sendraw(self, msg, priority=False, delay=None):
        if priority:
            self.msgqueue.appendleft((msg, delay))
        else:
            self.msgqueue.append((msg, delay))

    def sendmsg(self, name, msg, delay=None):
        for msgline in msg.split("\n"):
            if msgline != "":
                self.sendraw("PRIVMSG {} :{}\n".format(name, msgline), delay=delay)

    def joinchan(self, channel):
        self.sendraw("JOIN {}\n".format(channel))

    def invitechan(self, name, channel):
        self.sendraw("INVITE {} {}\n".format(name, channel), delay=1)

    def modes(self, channel, mode):
        self.sendraw("MODE {} {}\n".format(channel, mode), delay=2)

    def create_room(self, game_name):
        assigned_room = self.game_rooms.popleft()  # Todo: handle running out of rooms
        self.assigned_game_rooms[game_name] = assigned_room
        # Todo: add game options to topic
        self.sendmsg("chanserv", "TOPIC {} Coup game {}: Hosted by {}".format(assigned_room, game_name, self.botnick))
        logging.debug("Assigning room {}: {}".format(assigned_room, game_name))

    def add_player(self, name, game_name):
        assigned_room = self.assigned_game_rooms[game_name]
        self.invitechan(name, assigned_room)
        logging.debug("Adding player room {}: {}".format(assigned_room, name))

    def destroy_room(self, game_name):
        assigned_room = self.assigned_game_rooms[game_name]
        del self.assigned_game_rooms[game_name]
        self.game_rooms.append(assigned_room)
        logging.debug("Clearing room {}: {}".format(assigned_room, game_name))

    def identify(self, nick, password):
        self.sendraw("USER {0} {0} {0} {0}\n".format(nick))
        self.sendraw("NICK {}\n".format(nick), delay=2)
        if password is not None:
            self.sendraw("PASS {}\n".format(password), delay=2)
        self.sendmsg("nickserv", "identify {}".format(password), delay=25)

    def process_send_recv(self):
        # The limits are 5 line burst, 2 lines per second afterward. It is
        # implemented by giving you 2 credits a second, limited to 5. So if you
        # pause a second, you can do a 4 line burst. if the backlog exceeds 20
        # lines, you get killed for excess flood

        default_msg_delay = .5  # seconds of delay between messages
        ircmsg = None
        while ircmsg is None:
            # Process game's message queue
            if not self.msgqueue and self.parser.instance.msgqueue:
                msg_type, payload = self.parser.instance.msgqueue.popleft()
                if msg_type == "private message":
                    name, msg = payload
                    self.sendmsg(name, msg)
                elif msg_type == "game message":
                    name, msg = payload
                    irc_room = self.assigned_game_rooms[name]
                    self.sendmsg(irc_room, msg)
                elif msg_type == "create room":
                    self.create_room(payload)
                elif msg_type == "invite":
                    name, game_name = payload
                    self.add_player(name, game_name)
                elif msg_type == "destroy room":
                    self.destroy_room(payload)
                else:
                    logging.error("Unrecognized queue event type: {}, {}, {}".format(msg_type, name, msg))
                    raise TypeError
            # Send message
            if self.prevdelay is None:
                msg_delay = default_msg_delay
            else:
                msg_delay = self.prevdelay
            if self.msgqueue and time.time() - self.lastsent > msg_delay:
                msg, delay = self.msgqueue.popleft()
                self.lastsent = time.time()
                self.prevdelay = delay
                logging.debug(">> {}".format(msg))
                self.ircsocket.send(msg.encode("utf-8"))
            # Receive message
            try:
                ircmsg = self.ircsocket.recv(2048)
            except socket.error:
                pass
        return ircmsg.decode("utf-8").strip("\n\r")

    def run(self):
        logging.info("Listening")
        connected = True
        try:
            while connected:
                ircmsg = self.process_send_recv()
                logging.debug(ircmsg)
                matchstr = ":(?P<nick>.*)!(?P<user>.*)@(?P<host>.*) PRIVMSG (?P<sentto>.*) :\.(?P<command>.*)"
                privmsg = re.match(matchstr, ircmsg)
                if privmsg is not None:
                    message = {'nick': privmsg.group('nick'),
                               'user': privmsg.group('user'),
                               'host': privmsg.group('host'),
                               'sentto': privmsg.group('sentto'),
                               'command': privmsg.group('command'),
                               'raw': ircmsg,
                               'is_priv': privmsg.group('sentto') == self.botnick}
                    logging.info("{} << .{}".format(message['nick'], message['command']))
                    response = self.parser.parse_input(message)
                    if response is not None:
                        logging.info("{} >> {}".format(message['nick'], response))
                        self.sendmsg(message['nick'], response)
                matchstr = ":(?P<nick>.*)!(?P<user>.*)@(?P<host>.*) PART (?P<channel>.*)"
                partmsg = re.match(matchstr, ircmsg)
                if partmsg is not None:
                    pass  # TODO: Handle leavers
                if ircmsg.startswith("PING :"):
                    self.ping()
                if ircmsg.startswith("ERROR :"):
                    connected = False
        except KeyboardInterrupt:
            logging.info("Exiting: KeyboardInterrupt")
        else:
            logging.info("Exiting: {},{}".format(connected, ircmsg))
        self.disconnect()

    def ping(self):
        self.sendraw("PONG :pingis\n", priority=True)

    def disconnect(self):
        self.ircsocket.shutdown(socket.SHUT_RDWR)
        self.ircsocket.close()


def main():
    connection = irc_connection(parser=print,
                                channellist=["#coupbot"],
                                botnick="coupbot_testing",
                                server="chat.freenode.net",
                                usessl=False)
    connection.run()


if __name__ == "__main__":
    main()
