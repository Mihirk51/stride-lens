from abc import ABC, abstractmethod

from src.schemas.manual_sleep_and_recovery import ManualSleepInput


class SleepService(ABC):
    @abstractmethod
    def record_sleep(self, data: ManualSleepInput) -> dict:
        """Record sleep data and return standardized metrics"""
        pass
