from gamebot.coup.actions import Assassinate, ForeignAid, Steal, Tax, ExchangeTwo, ExchangeOne, Examine

__author__ = 'jswaro'


class Influence(object):
    def __init__(self, name, actions, counteractions):
        self.name = name
        self.actions = actions
        self.counteractions = counteractions

    def description(self):
        desc = ["Class: {}".format(self.name)]
        desc += ["Action: {}: {}".format(act.name, act.description) for act in self.actions]
        desc += ["Counter action: Blocks {}".format(act.name) for act in self.counteractions]
        return "/n".join(desc)

    def short_description(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

contessa = Influence("Contessa", actions=[], counteractions=[Assassinate])
duke = Influence("Duke", actions=[Tax], counteractions=[ForeignAid])
captain = Influence("Captain", actions=[Steal], counteractions=[Steal])
ambassador = Influence("Ambassador", actions=[ExchangeTwo], counteractions=[Steal])
assassin = Influence("Assassin", actions=[Assassinate], counteractions=[])
inquisitor = Influence("Inquisitor", actions=[ExchangeOne, Examine], counteractions=[Steal])