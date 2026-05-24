"""
Markdown 格式导出器

将代码知识图谱导出为结构化的 Markdown 报告。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph.builder import CodeGraph


class MarkdownExporter:
    """Markdown 格式导出器

    将代码知识图谱导出为结构化的 Markdown 报告。
    """

    def export(self, graph: "CodeGraph") -> str:
        """导出为 Markdown 字符串

        Args:
            graph: 代码知识图谱

        Returns:
            Markdown 格式的字符串
        """
        lines: list = []

        # 标题
        lines.append(f"# CodeGraph-Lite 分析报告")
        lines.append("")
        lines.append(f"**项目路径**: `{graph.project_path}`")
        lines.append("")

        # 导入分析模块
        from ..analyzer.complexity import ComplexityAnalyzer
        from ..analyzer.dependency import DependencyAnalyzer
        from ..analyzer.metrics import MetricsAnalyzer

        complexity = ComplexityAnalyzer(graph).analyze()
        dependency = DependencyAnalyzer(graph).analyze(detect_cycles=True)
        metrics = MetricsAnalyzer(graph).analyze()

        # 项目概览
        lines.append("## 项目概览")
        lines.append("")
        lines.append("| 指标 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| 文件数量 | {metrics['file_count']} |")
        lines.append(f"| 函数数量 | {metrics['function_count']} |")
        lines.append(f"| 类数量 | {metrics['class_count']} |")
        lines.append(f"| 导入数量 | {metrics['import_count']} |")
        lines.append(f"| 变量数量 | {metrics['variable_count']} |")
        lines.append(f"| 总代码行数 | {metrics['total_loc']} |")
        lines.append(f"| 平均函数复杂度 | {metrics['avg_function_complexity']} |")
        lines.append("")

        # 语言分布
        if metrics["files_by_language"]:
            lines.append("## 语言分布")
            lines.append("")
            lines.append("| 语言 | 文件数 |")
            lines.append("|------|--------|")
            for lang, count in metrics["files_by_language"].items():
                lines.append(f"| {lang} | {count} |")
            lines.append("")

        # 节点统计
        node_counts = graph.count_nodes_by_type()
        lines.append("## 节点统计")
        lines.append("")
        lines.append("| 类型 | 数量 |")
        lines.append("|------|------|")
        for ntype, count in sorted(node_counts.items()):
            lines.append(f"| {ntype} | {count} |")
        lines.append("")

        # 边统计
        edge_counts = graph.count_edges_by_type()
        lines.append("## 边统计")
        lines.append("")
        lines.append("| 类型 | 数量 |")
        lines.append("|------|------|")
        for etype, count in sorted(edge_counts.items()):
            lines.append(f"| {etype} | {count} |")
        lines.append("")

        # 复杂度分析
        lines.append("## 复杂度分析")
        lines.append("")
        lines.append(f"- **函数总数**: {complexity['total_functions']}")
        lines.append(f"- **平均复杂度**: {complexity['avg_complexity']}")
        lines.append(f"- **最大复杂度**: {complexity['max_complexity']}")
        lines.append("")

        # 风险分布
        risk = complexity["risk_distribution"]
        lines.append("### 风险等级分布")
        lines.append("")
        lines.append("| 等级 | 范围 | 数量 |")
        lines.append("|------|------|------|")
        lines.append(f"| 低风险 | 1-5 | {risk['low']} |")
        lines.append(f"| 中风险 | 6-10 | {risk['medium']} |")
        lines.append(f"| 高风险 | 11-20 | {risk['high']} |")
        lines.append(f"| 极高风险 | >20 | {risk['critical']} |")
        lines.append("")

        # Top 10 最复杂函数
        top_funcs = complexity["functions"][:10]
        if top_funcs:
            lines.append("### Top 10 最复杂函数")
            lines.append("")
            lines.append("| 排名 | 函数名 | 复杂度 | 文件 | 行号 |")
            lines.append("|------|--------|--------|------|------|")
            for i, func in enumerate(top_funcs, 1):
                import os
                fname = os.path.basename(func["file"])
                lines.append(
                    f"| {i} | `{func['name']}` | {func['complexity']} "
                    f"| {fname} | {func['line']} |"
                )
            lines.append("")

        # 依赖分析
        lines.append("## 依赖分析")
        lines.append("")
        lines.append(f"- **模块数量**: {dependency['module_count']}")
        lines.append(f"- **依赖边数**: {dependency['dependency_count']}")
        lines.append(f"- **最大依赖深度**: {dependency['max_depth']}")
        lines.append("")

        # 循环依赖
        if dependency["cycles"]:
            lines.append("### 循环依赖警告")
            lines.append("")
            for cycle in dependency["cycles"]:
                lines.append(f"- {' -> '.join(cycle)}")
            lines.append("")
        else:
            lines.append("### 循环依赖")
            lines.append("")
            lines.append("未检测到循环依赖。")
            lines.append("")

        # 被依赖最多的模块
        if dependency["most_depended"]:
            lines.append("### 被依赖最多的模块")
            lines.append("")
            lines.append("| 模块 | 被依赖次数 |")
            lines.append("|------|-----------|")
            for item in dependency["most_depended"]:
                lines.append(f"| `{item['module']}` | {item['count']} |")
            lines.append("")

        # 文件详情
        lines.append("## 文件详情")
        lines.append("")
        lines.append("| 文件 | LOC | 函数 | 类 | 导入 |")
        lines.append("|------|-----|------|-----|------|")
        for file_path, stats in sorted(metrics["file_stats"].items()):
            import os
            fname = os.path.basename(file_path)
            lines.append(
                f"| `{fname}` | {stats['loc']} | {stats['function_count']} "
                f"| {stats['class_count']} | {stats['import_count']} |"
            )
        lines.append("")

        return "\n".join(lines)
