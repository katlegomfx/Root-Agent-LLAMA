from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional

@dataclass
class Step:
    name: str
    action: callable
    params: Dict[str, Any]
    status: str = "Pending"  # Possible statuses: Pending, In Progress, Completed, Failed
    retries: int = 0
    max_retries: int = 3
    result: Optional[Any] = None

@dataclass
class SelfImprovementState:
    steps: List[Step] = field(default_factory=list)
    improvements: Dict[str, Any] = field(default_factory=dict)
    current_step_index: int = 0
    completed: bool = False
