import os
from typing import Any, Mapping, Tuple
import pvcobra as pvcobra

import numpy as np


class _StateMachine:
    """
    This class is responsible for the state of the call.
    Possible states:
    - call_pending
    - [waiting_in_queue]  # waiting_in_queue requirs a different strategy than waiting
    - start_opener_speaking
    - start_speaking
    - speaking
    - [waiting]
    - call_ended
    - call_interrupted
    """
    VALID_STATES = ["call_pending",
                    "waiting_in_queue",
                    "start_opener_speaking",
                    "speaking",
                    "start_speaking",
                    "waiting",
                    "call_ended",
                    "call_interrupted"]

    def __init__(self, max_counter_silence: int = 5) -> None:
        self.state = "call_pending"
        # "waiting" as a toggle, we check each "speech chunk" if the opposite is speaking
        #  if we are in "waiting", we transition to "speaking", once the counter reaches max_counter_silence
        #  "wait mode" is initated again, once our transcript is empty
        self.silence_counter = 0
        self.max_counter_silence = max_counter_silence

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, new_state) -> None:
        assert new_state in self.VALID_STATES, f"Invalid state {new_state}"
        self._state = new_state

    @property
    def silence_counter(self):
        return self._silence_counter

    @silence_counter.setter
    def silence_counter(self, new_counter=0):
        self._silence_counter = new_counter

    def inc_counter(self) -> bool:
        self.silence_counter += 1
        if self._silence_counter >= self.max_counter_silence:
            return True
        else:
            return False

    def reset_counter(self) -> None:
        self.silence_counter = 0

    def check_opposite_speaking(self) -> bool:
        pass
        # todo call logic to detect if opposite is speaking or not

    def synthesis_response(self):
        pass

    def check_call_goal_fulfilled(self) -> bool:
        pass
        # todo call logic to detect if call aim is fulfilled


class ChunkHandler:
    def __init__(self, chunk_config: Mapping[str, Any] = None):
        self.state_machine = _StateMachine(
            **chunk_config.get("state_machine_config")) if chunk_config else _StateMachine()
        self.wait_threshold = chunk_config.get("wait_threshold") if chunk_config else 0.2
        pv_access_key = os.environ.get("PICOVOICE_API_KEY")
        assert pv_access_key, "PICOVOICE_API_KEY environment variable not set"
        self.cobra = pvcobra.create(access_key=pv_access_key)

    def check_waiting(self, chunk: np.ndarray) -> bool:
        # todo: What object does cobra even expect
        if self.cobra.process(chunk) > self.wait_threshold:
            return True
        return False

    def check_speaking(self, chunk: np.ndarray) -> bool:
        return not self.check_waiting(chunk)

    def check_waiting_in_queue(self, chunk: np.ndarray) -> bool:
        # todo: implement proper queue detection
        return self.check_waiting(chunk)

    def _can_speak(self):
        can_speak = self.state_machine.inc_counter()
        if can_speak:
            if self.state_machine.state == "waiting_in_queue":
                self.state_machine.state = "start_opener_speaking"
            else:
                self.state_machine.state = "start_speaking"
            self.state_machine.reset_counter()
        else:
            self.state_machine.reset_counter()
        return can_speak

    def start_call(self):
        self.state_machine.state = "waiting_in_queue"

    def transition_to_wait(self):
        self.state_machine.state = "waiting"

    # todo: chunk implictly assumed to be from caller or receive, depending on state?
    #  should we support the case when caller and receiver talk simultanously?
    def process_chunk(self, chunk: np.ndarray) -> Tuple[np.ndarray, bool]:
        can_speak = False
        if self.state_machine.state == "call_pending":
            # we probably don't need to do any processing during call_pending
            pass
        elif self.state_machine.state == 'waiting_in_queue':
            if self.check_waiting_in_queue(chunk):
                can_speak = self._can_speak()
        elif self.state_machine.state == "speaking":
            # todo process chunks
            can_speak = True
        elif self.state_machine.state in ["start_speaking", "start_opener_speaking"]:
            can_speak = True
            self.state_machine.state = "speaking"
        elif self.state_machine.state == "waiting":
            if self.check_waiting(chunk):
                can_speak = self._can_speak()
        # todo: ending call
        return chunk, can_speak
