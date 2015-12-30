class BaseTeam(object):
    UNASSIGNED = 0


def same_team(target, source):
    return target.team == source.team and target.team != BaseTeam.UNASSIGNED  # TODO: Handle all same team

