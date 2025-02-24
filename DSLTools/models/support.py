from dataclasses import dataclass
from typing import Dict, Any
@dataclass
class MetaObject:
    syntax: Dict[str, Any]
    debug_info_dir: str