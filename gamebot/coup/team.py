class Team(object):
    UNASSIGNED = 0
    REFORMIST = 1
    LOYALIST = 2


def same_team(target, source):
    if target.team == Team.UNASSIGNED or source.team == Team.UNASSIGNED:
        return False
    return target.get_team() == source.get_team()
