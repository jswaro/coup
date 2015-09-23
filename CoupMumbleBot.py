from optparse import OptionParser
import logging
import threading
import time

import mumble


class MumbleBot(mumble.Bot):
    def __init__(self, name, parser):
        mumble.Bot.__init__(self, name)
        self.botname = name
        self.parser = parser

    def send_simple_message(self, user, message):
        to_user = self.get_user_by_name(user)

        if to_user is None:
            print "could not send message to user {0}".format(user)
            return
        for line in message.split('\n'):
            self.send_message(to_user, line.encode('ascii'))

    def send_batch_message(self, users, message):
        if message is not None and message != "":
            for user in users:
                try:
                    self.send_simple_message(user, message)
                except Exception as e:
                    print e
                    print '"', return_message, '"'

    def on_text_message(self, from_user, to_users, to_channels, tree_ids, message):
        template = "from_user:{}, to_users:{}, to_channels:{}, tree_ids:{}, message:{}"
        print template.format(from_user, to_users, to_channels, tree_ids, message)

        command_attempt = False
        if self.state.user in to_users and len(to_channels) == 0:
            command_attempt = True
        elif message[0] == '/':
            command_attempt = True
            message = message[1:]

        if command_attempt:
            return_message = self.parser.parse_input(from_user.name, self.send_simple_message, message)


'''
bot = MumbleBot(name = "JimBot")
bot.start(mumble.Server('Anbon.us'), 'JimBot')

while bot.is_connected:
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        bot.stop()
'''
