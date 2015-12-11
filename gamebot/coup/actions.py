__author__ = 'jswaro'


class Action(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

income = Action("Income", "Take 1 coin")
foreign_aid = Action("Foreign Aid", "Take 2 coins")
tax = Action("Tax", "Take 3 coins")
steal = Action("Steal", "Take 2 coins from another player")
assassinate = Action("Assassinate", "Pay 3 coins, choose player to lose influence")
exchange2 = Action("Exchange", "Take 2 cards, return 2 cards to court deck")
exchange1 = Action("Exchange", "Take 1 card, return 1 card to court deck")
examine = Action("Examine", "Choose player; look at one card, may force Exchange")
coup = Action("Coup", "Pay 7 coins, choose player to lose influence")
convert = Action("Convert",
                 "Change Allegiance.  Place 1 coin yourself or 2 coins for another player on Treasury Reserve")
embezzle = Action("Embezzle", "Take all coins from Treasury Reserve")