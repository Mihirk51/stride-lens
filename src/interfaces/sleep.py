from abc import ABC, abstractmethod

from src.schemas.manual_sleep_and_recovery_schema import (
    ManualSleepInput,
    ManualSleepServiceResponse,
)


class SleepService(ABC):
    @abstractmethod
    def record_sleep(self, data: ManualSleepInput) -> ManualSleepServiceResponse:
        """Record sleep data and return standardized metrics"""
        pass
