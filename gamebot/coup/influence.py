__author__ = 'jswaro'

from gamebot.coup.actions import assassinate, foreign_aid, steal, tax, exchange1, exchange2, examine


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

contessa = Influence("Contessa", actions=[], counteractions=[assassinate])
duke = Influence("Duke", actions=[tax], counteractions=[foreign_aid])
captain = Influence("Captain", actions=[steal], counteractions=[steal])
ambassador = Influence("Ambassador", actions=[exchange2], counteractions=[steal])
assassin = Influence("Assassin", actions=[assassinate], counteractions=[])
inquisitor = Influence("Inquisitor", actions=[exchange1, examine], counteractions=[steal])