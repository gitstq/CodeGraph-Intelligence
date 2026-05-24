"""
图谱节点定义

定义知识图谱中的节点类型和节点数据结构。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(str, Enum):
    """节点类型枚举"""
    MODULE = "Module"
    CLASS = "Class"
    FUNCTION = "Function"
    VARIABLE = "Variable"
    IMPORT = "Import"


@dataclass
class GraphNode:
    """知识图谱节点

    Attributes:
        id: 节点唯一标识符
        name: 节点名称
        node_type: 节点类型
        file_path: 所在文件路径
        line_start: 起始行号
        line_end: 结束行号
        docstring: 文档字符串
        metadata: 额外的元数据
    """
    id: str
    name: str
    node_type: NodeType
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    docstring: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "docstring": self.docstring,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        """从字典创建节点"""
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=NodeType(data["type"]),
            file_path=data.get("file_path", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            docstring=data.get("docstring", ""),
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphNode):
            return NotImplemented
        return self.id == other.id

    def __repr__(self) -> str:
        return f"GraphNode(id={self.id!r}, name={self.name!r}, type={self.node_type.value})"
