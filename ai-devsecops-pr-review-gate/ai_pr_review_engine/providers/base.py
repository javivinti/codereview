from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError
