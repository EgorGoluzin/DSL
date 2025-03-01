from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class TypeParse(str, Enum):
    RBNF = "rbnf"
    WIRTH = "wirth"
    UML = "uml"


@dataclass
class MetaObject:
    syntax: Dict[str, Any]
    debug_info_dir: str
    type_to_parse: TypeParse

    def __init__(self, mo_as_json):
        self.syntax = mo_as_json["syntax"]
        self.debug_info_dir = mo_as_json["debugInfoDir"]
        self.type_to_parse = mo_as_json["syntax"]["type"]
