class Team(object):
    NONE = 0
    RED = 1
    BLUE = 2


def same_team(target, source):
    if target.team == Team.NONE or source.team == Team.NONE:
        return False
    return target.get_team() == source.get_team()