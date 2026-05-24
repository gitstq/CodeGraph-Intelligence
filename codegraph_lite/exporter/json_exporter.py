"""
JSON 格式导出器

将代码知识图谱导出为 JSON 格式。
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph.builder import CodeGraph


class JsonExporter:
    """JSON 格式导出器

    将代码知识图谱导出为结构化的 JSON 格式。
    """

    def export(self, graph: "CodeGraph") -> str:
        """导出为 JSON 字符串

        Args:
            graph: 代码知识图谱

        Returns:
            JSON 格式的字符串
        """
        data = graph.to_dict()

        # 添加分析结果
        from ..analyzer.complexity import ComplexityAnalyzer
        from ..analyzer.dependency import DependencyAnalyzer
        from ..analyzer.metrics import MetricsAnalyzer

        complexity = ComplexityAnalyzer(graph).analyze()
        dependency = DependencyAnalyzer(graph).analyze(detect_cycles=True)
        metrics = MetricsAnalyzer(graph).analyze()

        data["analysis"] = {
            "complexity": {
                "total_functions": complexity["total_functions"],
                "avg_complexity": complexity["avg_complexity"],
                "max_complexity": complexity["max_complexity"],
                "risk_distribution": complexity["risk_distribution"],
                "top_complex_functions": complexity["functions"][:20],
            },
            "dependency": {
                "module_count": dependency["module_count"],
                "dependency_count": dependency["dependency_count"],
                "max_depth": dependency["max_depth"],
                "cycles": dependency["cycles"],
                "most_depended": dependency["most_depended"],
            },
            "metrics": {
                "total_loc": metrics["total_loc"],
                "file_count": metrics["file_count"],
                "function_count": metrics["function_count"],
                "class_count": metrics["class_count"],
                "import_count": metrics["import_count"],
                "avg_function_complexity": metrics["avg_function_complexity"],
                "files_by_language": metrics["files_by_language"],
            },
        }

        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
