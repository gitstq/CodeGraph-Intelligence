"""
知识图谱构建器

将解析结果转换为知识图谱，支持增量索引和缓存。
"""

import hashlib
import json
import os
from typing import Dict, List, Optional, Set, Tuple

from ..parser import get_parser
from ..parser.base import ParseResult
from ..utils.cache import FileCache
from .edge import EdgeType, GraphEdge
from .node import GraphNode, NodeType


class CodeGraph:
    """代码知识图谱

    存储代码项目的节点和边，提供查询和统计接口。
    """

    def __init__(self, project_path: str = ""):
        self.project_path = project_path
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[GraphEdge]] = {}
        self._reverse_adjacency: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> None:
        """添加节点"""
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """添加边"""
        self.edges.append(edge)
        # 更新邻接表
        if edge.source_id not in self._adjacency:
            self._adjacency[edge.source_id] = []
        self._adjacency[edge.source_id].append(edge)
        # 更新反向邻接表
        if edge.target_id not in self._reverse_adjacency:
            self._reverse_adjacency[edge.target_id] = []
        self._reverse_adjacency[edge.target_id].append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[GraphNode]:
        """获取相邻节点"""
        neighbors = []
        for edge in self._adjacency.get(node_id, []):
            node = self.nodes.get(edge.target_id)
            if node:
                neighbors.append(node)
        return neighbors

    def get_outgoing_edges(self, node_id: str) -> List[GraphEdge]:
        """获取出边"""
        return self._adjacency.get(node_id, [])

    def get_incoming_edges(self, node_id: str) -> List[GraphEdge]:
        """获取入边"""
        return self._reverse_adjacency.get(node_id, [])

    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """按类型获取节点"""
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_edges_by_type(self, edge_type: EdgeType) -> List[GraphEdge]:
        """按类型获取边"""
        return [e for e in self.edges if e.edge_type == edge_type]

    def count_nodes_by_type(self) -> Dict[str, int]:
        """统计各类型节点数量"""
        counts: Dict[str, int] = {}
        for node in self.nodes.values():
            type_name = node.node_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def count_edges_by_type(self) -> Dict[str, int]:
        """统计各类型边数量"""
        counts: Dict[str, int] = {}
        for edge in self.edges:
            type_name = edge.edge_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def get_files(self) -> Set[str]:
        """获取所有涉及的文件路径"""
        return {n.file_path for n in self.nodes.values() if n.file_path}

    def get_total_loc(self) -> int:
        """获取总代码行数"""
        total = 0
        for node in self.nodes.values():
            if node.line_end > 0 and node.line_start > 0:
                total += node.line_end - node.line_start + 1
        return total

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "project_path": self.project_path,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "nodes_by_type": self.count_nodes_by_type(),
                "edges_by_type": self.count_edges_by_type(),
            },
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CodeGraph":
        """从字典创建图谱"""
        graph = cls(project_path=data.get("project_path", ""))
        for node_data in data.get("nodes", []):
            graph.add_node(GraphNode.from_dict(node_data))
        for edge_data in data.get("edges", []):
            graph.add_edge(GraphEdge.from_dict(edge_data))
        return graph


class GraphBuilder:
    """知识图谱构建器

    将代码解析结果转换为知识图谱。
    支持增量索引和缓存。
    """

    def __init__(
        self,
        project_path: str = "",
        language: str = None,
        use_cache: bool = True,
    ):
        self.project_path = project_path
        self.language = language
        self.use_cache = use_cache
        self.cache = FileCache(project_path) if use_cache else None

    def build(self, files: List[str]) -> CodeGraph:
        """构建知识图谱

        Args:
            files: 要分析的文件列表

        Returns:
            构建好的代码知识图谱
        """
        graph = CodeGraph(project_path=self.project_path)

        # 添加项目根模块节点
        project_name = os.path.basename(self.project_path) or "root"
        graph.add_node(GraphNode(
            id=f"module:{project_name}",
            name=project_name,
            node_type=NodeType.MODULE,
            file_path=self.project_path,
        ))

        # 解析每个文件
        parse_results: List[ParseResult] = []
        for file_path in files:
            result = self._parse_file(file_path)
            if result:
                parse_results.append(result)

        # 将解析结果转换为图谱节点和边
        for result in parse_results:
            self._add_parse_result_to_graph(graph, result)

        # 构建模块间依赖关系
        self._build_module_dependencies(graph, parse_results)

        return graph

    def _parse_file(self, file_path: str) -> Optional[ParseResult]:
        """解析单个文件

        Args:
            file_path: 文件路径

        Returns:
            解析结果，如果解析失败返回 None
        """
        # 检查缓存 - 如果缓存命中且未过期，仍需完整解析
        # （缓存用于记录已扫描文件，避免重复写入）
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except (IOError, OSError):
            return None

        parser = get_parser(file_path, self.language)
        result = parser.parse(source, file_path)

        # 写入缓存（记录文件已解析）
        if self.cache:
            self.cache.set(file_path, result.summary())

        return result

    def _add_parse_result_to_graph(
        self, graph: CodeGraph, result: ParseResult
    ) -> None:
        """将解析结果添加到图谱中

        Args:
            graph: 代码知识图谱
            result: 解析结果
        """
        file_path = result.file_path
        # 生成文件模块ID
        rel_path = os.path.relpath(file_path, self.project_path)
        module_id = f"module:{rel_path}"

        # 添加文件模块节点
        graph.add_node(GraphNode(
            id=module_id,
            name=rel_path,
            node_type=NodeType.MODULE,
            file_path=file_path,
        ))

        # 项目根 -> 文件模块（包含关系）
        project_name = os.path.basename(self.project_path) or "root"
        graph.add_edge(GraphEdge(
            source_id=f"module:{project_name}",
            target_id=module_id,
            edge_type=EdgeType.CONTAINS,
        ))

        # 添加函数节点
        for func in result.functions:
            func_id = f"func:{rel_path}:{func.name}:{func.line_start}"
            graph.add_node(GraphNode(
                id=func_id,
                name=func.name,
                node_type=NodeType.FUNCTION,
                file_path=file_path,
                line_start=func.line_start,
                line_end=func.line_end,
                docstring=func.docstring,
                metadata={
                    "parameters": func.parameters,
                    "return_type": func.return_type,
                    "complexity": func.complexity,
                    "decorators": func.decorators,
                    "calls": func.calls,
                    **func.metadata,
                },
            ))
            # 模块 -> 函数（包含关系）
            graph.add_edge(GraphEdge(
                source_id=module_id,
                target_id=func_id,
                edge_type=EdgeType.CONTAINS,
            ))

        # 添加类节点
        for cls in result.classes:
            cls_id = f"class:{rel_path}:{cls.name}:{cls.line_start}"
            graph.add_node(GraphNode(
                id=cls_id,
                name=cls.name,
                node_type=NodeType.CLASS,
                file_path=file_path,
                line_start=cls.line_start,
                line_end=cls.line_end,
                docstring=cls.docstring,
                metadata={
                    "bases": cls.bases,
                    "methods": cls.methods,
                    "decorators": cls.decorators,
                    **cls.metadata,
                },
            ))
            # 模块 -> 类（包含关系）
            graph.add_edge(GraphEdge(
                source_id=module_id,
                target_id=cls_id,
                edge_type=EdgeType.CONTAINS,
            ))

            # 继承关系
            for base in cls.bases:
                graph.add_edge(GraphEdge(
                    source_id=cls_id,
                    target_id=f"class:*:{base}:*",
                    edge_type=EdgeType.INHERITS,
                    metadata={"base_name": base},
                ))

        # 添加导入节点
        for imp in result.imports:
            imp_id = f"import:{rel_path}:{imp.module}:{imp.line_start}"
            graph.add_node(GraphNode(
                id=imp_id,
                name=imp.name,
                node_type=NodeType.IMPORT,
                file_path=file_path,
                line_start=imp.line_start,
                line_end=imp.line_end,
                metadata={
                    "module": imp.module,
                    "alias": imp.alias,
                    "names": imp.names,
                    "is_from_import": imp.is_from_import,
                    **imp.metadata,
                },
            ))
            # 模块 -> 导入（包含关系）
            graph.add_edge(GraphEdge(
                source_id=module_id,
                target_id=imp_id,
                edge_type=EdgeType.CONTAINS,
            ))

        # 添加变量节点
        for var in result.variables:
            var_id = f"var:{rel_path}:{var.name}:{var.line_start}"
            graph.add_node(GraphNode(
                id=var_id,
                name=var.name,
                node_type=NodeType.VARIABLE,
                file_path=file_path,
                line_start=var.line_start,
                line_end=var.line_end,
                metadata={
                    "var_type": var.var_type,
                    "value": var.value,
                },
            ))
            # 模块 -> 变量（包含关系）
            graph.add_edge(GraphEdge(
                source_id=module_id,
                target_id=var_id,
                edge_type=EdgeType.CONTAINS,
            ))

        # 添加调用关系边
        for caller, callee, line_num in result.calls:
            caller_id = f"func:{rel_path}:{caller}:*"
            callee_id = f"func:*:{callee}:*"
            graph.add_edge(GraphEdge(
                source_id=caller_id,
                target_id=callee_id,
                edge_type=EdgeType.CALLS,
                metadata={"line": line_num},
            ))

    def _build_module_dependencies(
        self, graph: CodeGraph, results: List[ParseResult]
    ) -> None:
        """构建模块间的依赖关系

        Args:
            graph: 代码知识图谱
            results: 所有文件的解析结果
        """
        # 构建模块名映射
        module_map: Dict[str, str] = {}
        for node in graph.nodes.values():
            if node.node_type == NodeType.MODULE:
                # 用文件名（不含扩展名）作为键
                name = os.path.splitext(node.name)[0].replace(os.sep, ".")
                module_map[name] = node.id
                # 也用文件名（不含路径）作为键
                basename = os.path.splitext(os.path.basename(node.name))[0]
                module_map[basename] = node.id

        # 根据导入关系构建模块依赖
        for result in results:
            rel_path = os.path.relpath(result.file_path, self.project_path)
            source_module_id = f"module:{rel_path}"

            for imp in result.imports:
                module_name = imp.module
                # 尝试匹配目标模块
                target_id = None

                # 直接匹配
                if module_name in module_map:
                    target_id = module_map[module_name]
                else:
                    # 尝试部分匹配
                    for key, mid in module_map.items():
                        if module_name.endswith(key) or key.endswith(module_name):
                            target_id = mid
                            break

                if target_id and target_id != source_module_id:
                    graph.add_edge(GraphEdge(
                        source_id=source_module_id,
                        target_id=target_id,
                        edge_type=EdgeType.IMPORTS,
                        metadata={"import_module": module_name},
                    ))
