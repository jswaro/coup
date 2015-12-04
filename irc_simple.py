from __future__ import print_function
import socket
import ssl
import re
import logging

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
        logging.debug("Connecting...")
        if usessl:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsocket = ssl.wrap_socket(raw_socket)
            self.ircsocket.connect((server, port))
        else:
            self.ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsocket.connect((server, port))
        logging.debug("Identifying...")
        self.identify(botnick, botpass)
        logging.debug("Joining...")
        for channel in channellist:
            self.joinchan(channel)
        logging.debug("Done")

    def sendraw(self, msg):
        logging.debug(">> {}".format(msg))
        self.ircsocket.send(msg.encode("utf-8"))

    def sendmsg(self, name , msg):
        for msgline in msg.split("\n"):
            self.sendraw("PRIVMSG {} :{}\n".format(name, msgline))

    def joinchan(self, channel):
        self.sendraw("JOIN " + channel + "\n")

    def identify(self, nick, password):
        self.sendraw("USER {0} {0} {0} {0}\n".format(nick))
        self.sendraw("NICK {}\n".format(nick))
        if password is not None:
            self.sendraw("PASS {}\n".format(password))

    def run(self):
        logging.debug("Listening")
        connected = True
        try:
            while connected:
                ircmsg = self.ircsocket.recv(2048).decode("utf-8").strip("\n\r")
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
                    logging.debug("{}:{}:{}".format(message['sentto'], message['nick'], message['command']))
                    response = self.parser.parse_input(message, self.sendmsg)
                    if response is not None:
                        logging.info("{}: {}".format(message['nick'],response))
                        self.sendmsg(message['nick'], response)
                if ircmsg.startswith("PING :"):
                    self.ping()
                if ircmsg.startswith("ERROR :"):
                    connected = False
        except KeyboardInterrupt:
            logging.debug("Exiting: KeyboardInterrupt")
        else:
            logging.debug("Exiting: {},{}".format(connected,ircmsg))
        self.disconnect()

    def ping(self):
        self.sendraw("PONG :pingis\n")

    def disconnect(self):
        self.sendraw("QUIT :\n")
        ircmsg = self.ircsocket.recv(2048).decode("utf-8").strip("\n\r")
        logging.debug(ircmsg)
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
