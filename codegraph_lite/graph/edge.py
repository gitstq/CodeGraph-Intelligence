"""
图谱边定义

定义知识图谱中的边类型和边数据结构。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class EdgeType(str, Enum):
    """边类型枚举"""
    CALLS = "CALLS"           # 调用关系
    IMPORTS = "IMPORTS"       # 导入关系
    INHERITS = "INHERITS"     # 继承关系
    CONTAINS = "CONTAINS"     # 包含关系
    REFERENCES = "REFERENCES" # 引用关系


@dataclass
class GraphEdge:
    """知识图谱边

    Attributes:
        source_id: 源节点ID
        target_id: 目标节点ID
        edge_type: 边类型
        weight: 权重（可用于表示调用频率等）
        metadata: 额外的元数据
    """
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type.value,
            "weight": self.weight,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        """从字典创建边"""
        return cls(
            source_id=data["source"],
            target_id=data["target"],
            edge_type=EdgeType(data["type"]),
            weight=data.get("weight", 1),
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        return hash((self.source_id, self.target_id, self.edge_type))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphEdge):
            return NotImplemented
        return (
            self.source_id == other.source_id
            and self.target_id == other.target_id
            and self.edge_type == other.edge_type
        )

    def __repr__(self) -> str:
        return (
            f"GraphEdge({self.source_id!r} -[{self.edge_type.value}]-> "
            f"{self.target_id!r})"
        )
