from typing import NewType
from abc import ABC, abstractmethod


YamlString = NewType('YamlString', str)


class IYamlMedia(ABC):
    """Объект, преобразуемый в формат YAML."""
    @abstractmethod
    def to_yaml(self, offset: int = 0) -> YamlString:
        pass
