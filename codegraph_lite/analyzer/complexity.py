"""
代码复杂度分析模块

提供圈复杂度计算和复杂度排名功能。
"""

from typing import Any, Dict, List

from ..graph.builder import CodeGraph
from ..graph.node import NodeType


class ComplexityAnalyzer:
    """代码复杂度分析器

    分析代码知识图谱中各函数的圈复杂度，
    提供复杂度排名和统计信息。
    """

    def __init__(self, graph: CodeGraph):
        """初始化复杂度分析器

        Args:
            graph: 代码知识图谱
        """
        self.graph = graph

    def analyze(self) -> Dict[str, Any]:
        """执行复杂度分析

        Returns:
            包含以下键的字典：
            - total_functions: 函数总数
            - avg_complexity: 平均复杂度
            - max_complexity: 最大复杂度
            - min_complexity: 最小复杂度
            - functions: 按复杂度降序排列的函数列表
            - by_file: 按文件分组的复杂度统计
            - risk_distribution: 风险等级分布
        """
        functions = self._get_all_functions()

        if not functions:
            return {
                "total_functions": 0,
                "avg_complexity": 0,
                "max_complexity": 0,
                "min_complexity": 0,
                "functions": [],
                "by_file": {},
                "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            }

        complexities = [f["complexity"] for f in functions]
        avg = sum(complexities) / len(complexities)

        # 按复杂度降序排列
        functions.sort(key=lambda x: x["complexity"], reverse=True)

        # 按文件分组
        by_file: Dict[str, List[Dict]] = {}
        for func in functions:
            file_path = func["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(func)

        # 风险等级分布
        risk = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for c in complexities:
            if c <= 5:
                risk["low"] += 1
            elif c <= 10:
                risk["medium"] += 1
            elif c <= 20:
                risk["high"] += 1
            else:
                risk["critical"] += 1

        return {
            "total_functions": len(functions),
            "avg_complexity": round(avg, 1),
            "max_complexity": max(complexities),
            "min_complexity": min(complexities),
            "functions": functions,
            "by_file": by_file,
            "risk_distribution": risk,
        }

    def _get_all_functions(self) -> List[Dict[str, Any]]:
        """获取所有函数节点及其复杂度信息"""
        functions: List[Dict[str, Any]] = []

        for node in self.graph.nodes.values():
            if node.node_type == NodeType.FUNCTION:
                complexity = node.metadata.get("complexity", 1)
                functions.append({
                    "name": node.name,
                    "file": node.file_path,
                    "line": node.line_start,
                    "complexity": complexity,
                    "parameters": node.metadata.get("parameters", []),
                    "return_type": node.metadata.get("return_type", ""),
                    "calls": node.metadata.get("calls", []),
                    "decorators": node.metadata.get("decorators", []),
                })

        return functions

    def get_top_complex(self, n: int = 10) -> List[Dict[str, Any]]:
        """获取最复杂的N个函数

        Args:
            n: 返回数量

        Returns:
            最复杂的N个函数列表
        """
        result = self.analyze()
        return result["functions"][:n]

    def get_file_complexity(self, file_path: str) -> Dict[str, Any]:
        """获取指定文件的复杂度统计

        Args:
            file_path: 文件路径

        Returns:
            文件复杂度统计
        """
        result = self.analyze()
        file_funcs = result["by_file"].get(file_path, [])

        if not file_funcs:
            return {
                "file": file_path,
                "function_count": 0,
                "avg_complexity": 0,
                "max_complexity": 0,
                "functions": [],
            }

        complexities = [f["complexity"] for f in file_funcs]
        return {
            "file": file_path,
            "function_count": len(file_funcs),
            "avg_complexity": round(sum(complexities) / len(complexities), 1),
            "max_complexity": max(complexities),
            "functions": file_funcs,
        }
