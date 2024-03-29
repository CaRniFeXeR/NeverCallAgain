import os
import time
from typing import Any, Mapping, Tuple
import pvcobra as pvcobra

import numpy as np


# reminder flo credentials


def _get_energy(samples) -> float:
    # return np.sum(samples-np.min(samples))/(np.max(samples)-np.min(samples)) / float(len(samples))
    return np.sum(np.abs(samples) / 2147483647) / float(len(samples))
    # return np.sum(np.abs(samples)) / float(len(samples))


def _detect_silence(audio_chunk, silence_threshold):
    # max_energy = _get_energy([np.max(audio_chunk)])
    avg_energy = _get_energy(audio_chunk)
    # print(max_energy)
    # print("ratio: ", avg_energy / max_energy)
    print("avg energy: ", avg_energy)
    if avg_energy < silence_threshold:
        return True

    print("speak detected with energy: ", avg_energy)
    return False


class _StateMachine:
    """
    This class is responsible for the state of the call.
    Possible states:
    - call_pending
    - [waiting_in_queue]  # waiting_in_queue requirs a different strategy than waiting
    - start_opener_speaking
    - start_speaking
    - speaking
    - initator
    - call_ended
    - call_interrupted
    """
    # pov initator
    VALID_STATES = ["call_pending",
                    "waiting_in_queue",
                    "start_opener_speaking",
                    "speaking",
                    "start_speaking",
                    "listening",
                    "call_ended",
                    "call_interrupted"]

    # assuming 0.25 seconds per chunk, 1 second of silence is 4 chunks
    def __init__(self, max_silence_counter: int = 3, max_speaker_counter: int = 1) -> None:
        self.state = "call_pending"
        # "listening" as a toggle, we check each "speech chunk" if the opposite is speaking
        #  if we are in "listening", we transition to "speaking", once the counter reaches max_counter_silence
        #  "wait mode" is initated again, once our transcript is empty
        self.receiver_silence_counter = 0
        self.receiver_speaker_counter = 0
        self.max_receiver_silence_counter = max_silence_counter
        self.max_receiver_speaker_counter = max_speaker_counter

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, new_state) -> None:
        assert new_state in self.VALID_STATES, f"Invalid state {new_state}"
        if hasattr(self, "_state"):
            assert self._state != "call_ended", "Call has already ended"
        curr_state = self._state if hasattr(self, "_state") else "Init state"
        print("Transitioning from state {} to state {}".format(curr_state, new_state))
        self._state = new_state

    @property
    def receiver_silence_counter(self):
        return self._silence_counter

    @receiver_silence_counter.setter
    def receiver_silence_counter(self, new_counter=0):
        self._silence_counter = new_counter

    @property
    def receiver_speaker_counter(self):
        return self._speaker_counter

    @receiver_speaker_counter.setter
    def receiver_speaker_counter(self, new_counter=0):
        self._speaker_counter = new_counter

    def inc_receiver_silence_counter(self) -> None:
        print("Incrementing silence counter")
        self.receiver_silence_counter += 1

    def inc_receiver_speaking_counter(self) -> None:
        print("Incrementing speaking counter")
        self.receiver_speaker_counter += 1

    def reset_receiver_silence_counter(self) -> None:
        self._silence_counter = 0

    def reset_receiver_speaking_counter(self) -> None:
        self._speaker_counter = 0

    def synthesis_response(self):
        pass

    def check_call_goal_fulfilled(self) -> bool:
        pass
        # todo call logic to detect if call aim is fulfilled


class ChunkHandler:
    def __init__(self, chunk_config: Mapping[str, Any] = None):
        if chunk_config is None:
            chunk_config = dict()
        self.state_machine = _StateMachine(
            **chunk_config.get("state_machine_config")) if chunk_config else _StateMachine()
        self.wait_threshold = chunk_config.get("wait_threshold", 0.008)
        self.is_mono = chunk_config.get("is_mono", True)
        pv_access_key = os.environ.get("PICOVOICE_API_KEY")
        # assert pv_access_key, "PICOVOICE_API_KEY environment variable not set"
        # self.cobra = pvcobra.create(access_key=pv_access_key)
        self.chunk_length = chunk_config.get("chunk_length", 4000)

    @staticmethod
    def is_silent_chunk(
            audio_chunk: np.ndarray,
            is_mono: bool = True,
            silence_threshold_ratio: float = 0.1,
    ) -> bool:
        if not is_mono:
            audio_chunk = np.sum(audio_chunk, axis=1) / 2

        return _detect_silence(audio_chunk, silence_threshold_ratio)

    def handle_initator_waiting(self, chunk: np.ndarray) -> bool:
        """
            Checks whether the receiver is silent and updates the state machine accordingly
        """
        receiver_silent = self.is_silent_chunk(chunk, is_mono=self.is_mono, silence_threshold_ratio=self.wait_threshold)
        if receiver_silent:
            self.state_machine.inc_receiver_silence_counter()
        else:
            self.state_machine.reset_receiver_silence_counter()
        return receiver_silent

    def handle_receiver_speaking(self, chunk: np.ndarray) -> bool:
        """
            Checks whether the receiver is speaking and updates the state machine accordingly
        """
        receiver_speaking = not self.is_silent_chunk(chunk, is_mono=self.is_mono,
                                                     silence_threshold_ratio=self.wait_threshold)
        if receiver_speaking:
            self.state_machine.inc_receiver_speaking_counter()
        else:
            self.state_machine.reset_receiver_speaking_counter()
        return receiver_speaking

    def handle_queue_wait(self, chunk: np.ndarray) -> bool:
        # todo: implement proper queue detection
        return self.handle_initator_waiting(chunk)

    def _can_resume_speaking(self):
        can_speak = self.state_machine.receiver_silence_counter >= self.state_machine.max_receiver_silence_counter
        if can_speak:
            if self.state_machine.state == "waiting_in_queue":
                self.state_machine.state = "start_opener_speaking"
            else:
                self.state_machine.state = "start_speaking"
            self.state_machine.reset_receiver_silence_counter()
        return can_speak

    def _should_stop_speaking(self):
        should_stop = self.state_machine.receiver_speaker_counter >= self.state_machine.max_receiver_speaker_counter
        if should_stop:
            self.state_machine.state = "listening"
            self.state_machine.reset_receiver_speaking_counter()
        return should_stop

    def start_call(self):
        # TODO queue waiting skipped for now ..
        self.state_machine.state = "start_opener_speaking"

    def transition_to_end(self):
        self.state_machine.state = "call_ended"

    # todo: chunk implictly assumed to be from caller or receive, depending on state?
    #  should we support the case when caller and receiver talk simultanously?
    def process_chunk(self, chunk: np.ndarray) -> Tuple[np.ndarray, bool]:
        # Problem: Transitions from "speaking" to "listening" too early
        can_speak = False
        if self.state_machine.state == "call_pending":
            # we probably don't need to do any processing during call_pending
            pass
        elif self.state_machine.state == 'waiting_in_queue':
            if self.handle_queue_wait(chunk):
                can_speak = self._can_resume_speaking()
        elif self.state_machine.state == "speaking":
            # when initator is speaking, we need to check if the receiver is silent
            if self.handle_receiver_speaking(chunk):
                can_speak = not self._should_stop_speaking()
        elif self.state_machine.state in ["start_speaking", "start_opener_speaking"]:
            can_speak = True
            self.state_machine.state = "speaking"
        elif self.state_machine.state == "listening":
            if self.handle_initator_waiting(chunk):
                can_speak = self._can_resume_speaking()
        elif self.state_machine == "call_ended":
            can_speak = False
        # todo: ending call
        return chunk, can_speak
