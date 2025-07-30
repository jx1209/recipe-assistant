"""
Advanced Cooking Timer System
Supports multi-step cooking timers with pause, resume, and cancel features.
"""

import re
import threading
import time
import uuid
from typing import Callable, List, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)


class TimerStatus:
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StepTimer:
    def __init__(
        self,
        step_index: int,
        duration_seconds: int,
        description: str,
        on_start: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        tick_interval: int = 1,
    ):
        self.id = str(uuid.uuid4())
        self.step_index = step_index
        self.duration_seconds = duration_seconds
        self.remaining_seconds = duration_seconds
        self.description = description
        self.on_start = on_start
        self.on_tick = on_tick
        self.on_complete = on_complete
        self.tick_interval = tick_interval

        self.status = TimerStatus.PENDING
        self._thread = None
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        if self.status in {TimerStatus.COMPLETED, TimerStatus.CANCELLED}:
            return
        self.status = TimerStatus.RUNNING
        self._pause_event.set()
        self._cancel_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        if self.on_start:
            self.on_start(self)

    def _run(self):
        logging.info(f"🕒 Timer started for step {self.step_index + 1}: {self.description}")
        while self.remaining_seconds > 0 and not self._cancel_event.is_set():
            self._pause_event.wait()
            time.sleep(self.tick_interval)
            with self._lock:
                self.remaining_seconds -= self.tick_interval
                if self.on_tick:
                    self.on_tick(self)
        if not self._cancel_event.is_set():
            self.status = TimerStatus.COMPLETED
            logging.info(f"✅ Timer completed for step {self.step_index + 1}: {self.description}")
            if self.on_complete:
                self.on_complete(self)

    def pause(self):
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED
            self._pause_event.clear()
            logging.info(f"⏸️ Timer paused: {self.description}")

    def resume(self):
        if self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING
            self._pause_event.set()
            logging.info(f"▶️ Timer resumed: {self.description}")

    def cancel(self):
        if self.status in {TimerStatus.COMPLETED, TimerStatus.CANCELLED}:
            return
        self.status = TimerStatus.CANCELLED
        self._cancel_event.set()
        logging.info(f"❌ Timer cancelled: {self.description}")

    def get_state(self) -> Dict:
        return {
            "id": self.id,
            "step_index": self.step_index,
            "description": self.description,
            "remaining_seconds": max(0, self.remaining_seconds),
            "duration_seconds": self.duration_seconds,
            "status": self.status
        }


class CookingTimerManager:
    TIME_PATTERN = re.compile(r"(?:\bfor\b\s*)?(\d+)\s*(seconds|minutes|hours?)", re.IGNORECASE)

    def __init__(self):
        self.timers: Dict[str, StepTimer] = {}

    def extract_duration(self, step_text: str) -> Optional[int]:
        match = self.TIME_PATTERN.search(step_text)
        if not match:
            return None
        value, unit = match.groups()
        value = int(value)
        unit = unit.lower()

        if "hour" in unit:
            return value * 3600
        elif "minute" in unit:
            return value * 60
        elif "second" in unit:
            return value
        return None

    def create_timers(
        self,
        steps: List[str],
        on_start: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        on_complete: Optional[Callable] = None
    ) -> List[StepTimer]:
        self.timers = {}
        for idx, step in enumerate(steps):
            duration = self.extract_duration(step)
            if duration:
                timer = StepTimer(
                    step_index=idx,
                    duration_seconds=duration,
                    description=step,
                    on_start=on_start,
                    on_tick=on_tick,
                    on_complete=on_complete
                )
                self.timers[timer.id] = timer
        return list(self.timers.values())

    def start_all(self):
        for timer in self.timers.values():
            timer.start()

    def pause_timer(self, timer_id: str):
        if timer := self.timers.get(timer_id):
            timer.pause()

    def resume_timer(self, timer_id: str):
        if timer := self.timers.get(timer_id):
            timer.resume()

    def cancel_timer(self, timer_id: str):
        if timer := self.timers.get(timer_id):
            timer.cancel()

    def get_all_states(self) -> List[Dict]:
        return [t.get_state() for t in self.timers.values()]
