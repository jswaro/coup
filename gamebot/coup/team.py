from gamebot.game.team import BaseTeam


class Team(BaseTeam):
    REFORMIST = 1
    LOYALIST = 2


def same_team(target, source):

    if target.team == Team.UNASSIGNED or source.team == Team.UNASSIGNED:
        return False
    return target.team == source.team
