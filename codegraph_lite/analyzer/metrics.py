"""
代码度量指标模块

提供代码行数统计、函数/类数量、平均复杂度等度量指标。
"""

from typing import Any, Dict, List

from ..graph.builder import CodeGraph
from ..graph.node import NodeType


class MetricsAnalyzer:
    """代码度量指标分析器

    计算代码项目的各种度量指标，包括 LOC、函数数量、
    类数量、平均复杂度、依赖深度等。
    """

    def __init__(self, graph: CodeGraph):
        """初始化度量分析器

        Args:
            graph: 代码知识图谱
        """
        self.graph = graph

    def analyze(self) -> Dict[str, Any]:
        """执行度量分析

        Returns:
            包含以下键的字典：
            - total_loc: 总代码行数
            - file_count: 文件数量
            - function_count: 函数数量
            - class_count: 类数量
            - import_count: 导入数量
            - variable_count: 变量数量
            - avg_function_complexity: 平均函数复杂度
            - avg_functions_per_file: 每文件平均函数数
            - avg_classes_per_file: 每文件平均类数
            - files_by_language: 按语言分组的文件数
            - top_files_by_loc: 按LOC排序的文件列表
        """
        # 获取所有文件
        files = self.graph.get_files()
        file_count = len(files)

        # 按节点类型统计
        functions = self.graph.get_nodes_by_type(NodeType.FUNCTION)
        classes = self.graph.get_nodes_by_type(NodeType.CLASS)
        imports = self.graph.get_nodes_by_type(NodeType.IMPORT)
        variables = self.graph.get_nodes_by_type(NodeType.VARIABLE)

        function_count = len(functions)
        class_count = len(classes)
        import_count = len(imports)
        variable_count = len(variables)

        # 计算总LOC（基于文件）
        total_loc = self._calc_total_loc()

        # 平均函数复杂度
        complexities = [
            n.metadata.get("complexity", 1)
            for n in functions
        ]
        avg_complexity = (
            round(sum(complexities) / len(complexities), 1)
            if complexities
            else 0
        )

        # 按文件统计
        file_stats = self._calc_file_stats()

        # 按语言分组
        files_by_language = self._group_files_by_language()

        # 按LOC排序的文件
        top_files_by_loc = sorted(
            file_stats.items(),
            key=lambda x: x[1]["loc"],
            reverse=True,
        )[:20]

        return {
            "total_loc": total_loc,
            "file_count": file_count,
            "function_count": function_count,
            "class_count": class_count,
            "import_count": import_count,
            "variable_count": variable_count,
            "avg_function_complexity": avg_complexity,
            "avg_functions_per_file": (
                round(function_count / file_count, 1) if file_count else 0
            ),
            "avg_classes_per_file": (
                round(class_count / file_count, 1) if file_count else 0
            ),
            "files_by_language": files_by_language,
            "file_stats": file_stats,
            "top_files_by_loc": top_files_by_loc,
        }

    def _calc_total_loc(self) -> int:
        """计算总代码行数

        基于函数和类的行范围来估算。
        """
        total = 0
        for node in self.graph.nodes.values():
            if node.node_type in (NodeType.FUNCTION, NodeType.CLASS):
                if node.line_end > 0 and node.line_start > 0:
                    total += node.line_end - node.line_start + 1
        return total

    def _calc_file_stats(self) -> Dict[str, Dict[str, Any]]:
        """计算每个文件的统计信息"""
        file_stats: Dict[str, Dict[str, Any]] = {}

        for node in self.graph.nodes.values():
            fp = node.file_path
            if not fp:
                continue

            if fp not in file_stats:
                file_stats[fp] = {
                    "loc": 0,
                    "function_count": 0,
                    "class_count": 0,
                    "import_count": 0,
                    "variable_count": 0,
                }

            if node.node_type == NodeType.FUNCTION:
                file_stats[fp]["function_count"] += 1
                if node.line_end > 0 and node.line_start > 0:
                    file_stats[fp]["loc"] += (
                        node.line_end - node.line_start + 1
                    )
            elif node.node_type == NodeType.CLASS:
                file_stats[fp]["class_count"] += 1
                if node.line_end > 0 and node.line_start > 0:
                    file_stats[fp]["loc"] += (
                        node.line_end - node.line_start + 1
                    )
            elif node.node_type == NodeType.IMPORT:
                file_stats[fp]["import_count"] += 1
            elif node.node_type == NodeType.VARIABLE:
                file_stats[fp]["variable_count"] += 1

        return file_stats

    def _group_files_by_language(self) -> Dict[str, int]:
        """按语言分组文件"""
        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".mjs": "JavaScript",
            ".cjs": "JavaScript",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
        }

        lang_counts: Dict[str, int] = {}
        for fp in self.graph.get_files():
            import os
            ext = os.path.splitext(fp)[1].lower()
            lang = lang_map.get(ext, "Other")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        return dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True))

    def get_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """获取指定文件的度量指标

        Args:
            file_path: 文件路径

        Returns:
            文件度量指标
        """
        all_metrics = self.analyze()
        return all_metrics["file_stats"].get(file_path, {
            "loc": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0,
            "variable_count": 0,
        })
