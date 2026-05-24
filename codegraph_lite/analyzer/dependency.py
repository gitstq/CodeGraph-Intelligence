"""
依赖关系分析模块

提供模块依赖图分析、循环依赖检测和依赖深度计算。
"""

from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple

from ..graph.builder import CodeGraph
from ..graph.edge import EdgeType
from ..graph.node import NodeType


class DependencyAnalyzer:
    """依赖关系分析器

    分析代码知识图谱中的模块依赖关系，
    检测循环依赖，计算依赖深度。
    """

    def __init__(self, graph: CodeGraph):
        """初始化依赖分析器

        Args:
            graph: 代码知识图谱
        """
        self.graph = graph

    def analyze(self, detect_cycles: bool = True) -> Dict[str, Any]:
        """执行依赖分析

        Args:
            detect_cycles: 是否检测循环依赖

        Returns:
            包含以下键的字典：
            - module_count: 模块数量
            - dependency_count: 依赖边数量
            - max_depth: 最大依赖深度
            - cycles: 循环依赖列表
            - dependency_tree: 依赖关系树
            - orphan_modules: 无依赖的模块
            - most_depended: 被依赖最多的模块
        """
        # 获取模块依赖图
        dep_graph = self._build_dependency_graph()
        module_count = len(dep_graph)
        dependency_count = sum(len(deps) for deps in dep_graph.values())

        # 计算依赖深度
        max_depth = self._calc_max_depth(dep_graph)

        # 检测循环依赖
        cycles: List[List[str]] = []
        if detect_cycles:
            cycles = self._detect_cycles(dep_graph)

        # 构建依赖树
        dependency_tree: Dict[str, List[str]] = {}
        for module, deps in sorted(dep_graph.items()):
            dependency_tree[module] = sorted(deps)

        # 找出无依赖的模块
        all_targets: Set[str] = set()
        for deps in dep_graph.values():
            all_targets.update(deps)
        orphan_modules = sorted(
            m for m in dep_graph if m not in all_targets and not dep_graph[m]
        )

        # 被依赖最多的模块
        dep_count: Dict[str, int] = defaultdict(int)
        for deps in dep_graph.values():
            for dep in deps:
                dep_count[dep] += 1
        most_depended = sorted(
            dep_count.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "module_count": module_count,
            "dependency_count": dependency_count,
            "max_depth": max_depth,
            "cycles": cycles,
            "dependency_tree": dependency_tree,
            "orphan_modules": orphan_modules,
            "most_depended": [
                {"module": m, "count": c} for m, c in most_depended
            ],
        }

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """构建模块依赖图

        Returns:
            模块 -> 依赖模块集合 的映射
        """
        dep_graph: Dict[str, Set[str]] = defaultdict(set)

        # 从 IMPORTS 边构建依赖图
        for edge in self.graph.get_edges_by_type(EdgeType.IMPORTS):
            source_name = self._get_module_name(edge.source_id)
            target_name = self._get_module_name(edge.target_id)
            if source_name and target_name:
                dep_graph[source_name].add(target_name)

        # 确保所有模块都在图中
        for node in self.graph.get_nodes_by_type(NodeType.MODULE):
            dep_graph[node.name]  # 触发默认值创建

        return dict(dep_graph)

    def _get_module_name(self, node_id: str) -> str:
        """从节点ID中提取模块名"""
        if node_id.startswith("module:"):
            return node_id[7:]
        return ""

    def _calc_max_depth(self, dep_graph: Dict[str, Set[str]]) -> int:
        """计算最大依赖深度（使用BFS）

        Args:
            dep_graph: 依赖图

        Returns:
            最大依赖深度
        """
        if not dep_graph:
            return 0

        max_depth = 0
        for start in dep_graph:
            # BFS 计算从每个模块出发的最大深度
            visited: Set[str] = set()
            queue: deque = deque([(start, 0)])
            while queue:
                module, depth = queue.popleft()
                if module in visited:
                    continue
                visited.add(module)
                max_depth = max(max_depth, depth)
                for dep in dep_graph.get(module, set()):
                    if dep not in visited:
                        queue.append((dep, depth + 1))

        return max_depth

    def _detect_cycles(self, dep_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """检测循环依赖（使用DFS）

        Args:
            dep_graph: 依赖图

        Returns:
            循环依赖路径列表
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in dep_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for module in dep_graph:
            if module not in visited:
                dfs(module)

        return cycles

    def get_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """获取指定模块的依赖信息

        Args:
            module_name: 模块名

        Returns:
            模块依赖信息
        """
        dep_graph = self._build_dependency_graph()

        # 直接依赖
        direct_deps = dep_graph.get(module_name, set())

        # 反向依赖（谁依赖了这个模块）
        reverse_deps: Set[str] = set()
        for mod, deps in dep_graph.items():
            if module_name in deps:
                reverse_deps.add(mod)

        # 传递依赖
        transitive_deps: Set[str] = set()
        queue = deque(direct_deps)
        visited: Set[str] = set(direct_deps)
        while queue:
            current = queue.popleft()
            for dep in dep_graph.get(current, set()):
                if dep not in visited:
                    visited.add(dep)
                    transitive_deps.add(dep)
                    queue.append(dep)

        return {
            "module": module_name,
            "direct_dependencies": sorted(direct_deps),
            "reverse_dependencies": sorted(reverse_deps),
            "transitive_dependencies": sorted(transitive_deps),
            "direct_count": len(direct_deps),
            "reverse_count": len(reverse_deps),
            "transitive_count": len(transitive_deps),
        }
