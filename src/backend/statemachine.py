class StateMachine:
    """
    This class is responsible for the state of the call.
    Possible states:
    - call_pending
    - [waiting_in_queue]
    - speaking
    - listening
    - call_ended
    - call_interrupted
    """

    def __init__(self) -> None:
        self.state = "call_pending"

    def check_opposite_speaking(self) -> bool:
        pass
        # todo call logic to detect if opposite is speaking or not

    def synthesis_response(self):
        pass

    def check_call_goal_fulfilled(self) -> bool:
        pass
        # todo call logic to detect if call aim is fulfilled
