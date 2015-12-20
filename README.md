# coup
A python IRC bot for coup

This bot is intended to serve as a host for human played games of coup. 

# IRC Simple

To use the irc bot, you'll want to make sure to register and take ownership of a room to give you higher flood limits.
To do this automatically, you can set ``register=True`` and your email in the irc_simple.py program.
This will do the following:

* Register your bot with the server using the provided password and email
* Register your main channel and 10 game room channels and sets the bot as operator
* Set those channels to registered users only


Travis CI: [![Build Status](https://travis-ci.org/jswaro/coup.svg)](https://travis-ci.org/jswaro/coup)

