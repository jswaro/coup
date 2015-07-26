#!/bin/python
import os
import sys
import git

mumble_path = os.getcwd() + os.sep + 'mumble-bots'
if not os.path.exists(mumble_path):
	git.Git().clone('git://github.com/hansl/mumble-bots.git')

		

sys.path.append(mumble_path)

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

	def on_text_message(self, from_user, to_users, to_channels, tree_ids, message):

		if self.state.user in to_users and len(to_channels) == 0:
			self.parser.parse_input(from_user, message)
			#self.send_message(from_user, "Echo: " +message)
	

'''
bot = MumbleBot(name = "JimBot")
bot.start(mumble.Server('Anbon.us'), 'JimBot')

while bot.is_connected:
	try:	
		time.sleep(5)
	except KeyboardInterrupt:
		bot.stop()
'''
