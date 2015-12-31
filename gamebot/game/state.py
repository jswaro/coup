from collections import defaultdict

class InvalidStateTransition(Exception):
    pass

class StateTransitionActions(object):
    STA_NONE = 0
    STA_ACTION = 1
    STA_COUNTER = 2
    STA_CHALLENGE = 3
    STA_ACCEPT = 4
    STA_SELECT = 5
    STA_TIMEOUT = 6
    STA_FINISHED = 7

class StateMachine(object):
    STATE_INVALID_TRANSITION = -1
    STATE_GAME_START = 0
    STATE_TURN_START = 1
    STATE_ADVANCE_TURN = 2
    STATE_PLAYER_ACTION = 3
    #STATE_WAIT_PLAYER_RESPONSE = 4
    STATE_PLAYER_CHALLENGE = 5
    STATE_PLAYER_COUNTER = 6
    STATE_PLAYER_ACCEPT = 7
    STATE_PLAYER_SELECT = 8
    STATE_GAME_END = 9

    @staticmethod
    def invalid_transition():
        raise InvalidStateTransition


factory = lambda x: StateMachine.STATE_INVALID_TRANSITION

__stm = defaultdict(default_factory=factory)

# define default states
__stm[StateMachine.STATE_GAME_START] = { StateTransitionActions.STA_NONE : StateMachine.STATE_TURN_START }

__stm[StateMachine.STATE_TURN_START] = { StateTransitionActions.STA_ACTION : StateMachine.STATE_PLAYER_ACTION,
                                         StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_ADVANCE_TURN }

__stm[StateMachine.STATE_ADVANCE_TURN] = { StateTransitionActions.STA_NONE : StateMachine.STATE_TURN_START,
                                           StateTransitionActions.STA_FINISHED : StateMachine.STATE_GAME_END }

__stm[StateMachine.STATE_PLAYER_ACTION] = { StateTransitionActions.STA_NONE : StateMachine.STATE_ADVANCE_TURN,
                                            StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_ADVANCE_TURN,
                                            StateTransitionActions.STA_CHALLENGE : StateMachine.STATE_PLAYER_CHALLENGE,
                                            StateTransitionActions.STA_COUNTER : StateMachine.STATE_PLAYER_COUNTER,
                                            StateTransitionActions.STA_ACCEPT : StateMachine.STATE_PLAYER_ACCEPT,
                                            StateTransitionActions.STA_SELECT : StateMachine.STATE_PLAYER_SELECT }

__stm[StateMachine.STATE_PLAYER_CHALLENGE] = { StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_PLAYER_ACCEPT,
                                               StateTransitionActions.STA_SELECT : StateMachine.STATE_PLAYER_SELECT }

__stm[StateMachine.STATE_PLAYER_COUNTER] = { StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_PLAYER_ACCEPT,
                                             StateTransitionActions.STA_ACCEPT : StateMachine.STATE_PLAYER_ACCEPT,
                                             StateTransitionActions.STA_CHALLENGE : StateMachine.STATE_PLAYER_CHALLENGE }

__stm[StateMachine.STATE_PLAYER_ACCEPT] = { StateTransitionActions.STA_NONE : StateMachine.STATE_ADVANCE_TURN,
                                            StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_ADVANCE_TURN }

__stm[StateMachine.STATE_PLAYER_SELECT] = { StateTransitionActions.STA_TIMEOUT : StateMachine.STATE_ADVANCE_TURN,
                                            StateTransitionActions.STA_NONE : StateMachine.STATE_ADVANCE_TURN }

print(__stm)