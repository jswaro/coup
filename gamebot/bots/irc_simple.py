from __future__ import print_function

import logging
import re
import socket
import ssl
import time
from collections import deque


class irc_connection():
    def __init__(self, parser, channellist, botnick, botpass=None, server='chat.freenode.net', usessl=True, port=None):
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
            self.ircsocket.connect((server, port))
        else:
            self.ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsocket.connect((server, port))
        self.ircsocket.setblocking(False)
        self.identify(botnick, botpass)
        for channel in channellist:
            self.joinchan(channel)

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
        self.sendraw("JOIN " + channel + "\n")

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
                msg_type, name, msg = self.parser.instance.msgqueue.popleft()
                if msg_type in ("private message", "game message"):
                    self.sendmsg(self, name, msg)
                if msg_type == "invite":
                    pass  # TODO
                if msg_type == "create room":
                    pass  # TODO
                else:
                    logging.error("Unrecognized message type: {}, {}, {}".format(msg_type, name, msg))
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
