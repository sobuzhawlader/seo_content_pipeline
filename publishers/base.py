from abc import ABC, abstractmethod
from typing import Any

class BasePublisher(ABC):
    @abstractmethod
    def publish(self, *args: Any, **kwargs: Any) -> str:
        """Publishes the article payload to the target platform and returns the published URL or reference."""
        pass
