"""
交互式 TUI 仪表盘

使用 ANSI 转义码实现彩色终端界面，显示项目概览、
复杂度热力图、依赖关系树和 Top 10 最复杂函数。
"""

import os
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ..graph.builder import CodeGraph


# ANSI 颜色码
class Color:
    """ANSI 颜色码常量"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"


class Dashboard:
    """交互式 TUI 仪表盘

    在终端中渲染彩色的项目分析仪表盘。
    """

    def __init__(self, graph: "CodeGraph", project_path: str = ""):
        """初始化仪表盘

        Args:
            graph: 代码知识图谱
            project_path: 项目路径
        """
        self.graph = graph
        self.project_path = project_path
        self.project_name = os.path.basename(project_path) or "Project"
        self.width = self._get_terminal_width()

    def render(self) -> None:
        """渲染完整的仪表盘"""
        # 导入分析模块
        from ..analyzer.complexity import ComplexityAnalyzer
        from ..analyzer.dependency import DependencyAnalyzer
        from ..analyzer.metrics import MetricsAnalyzer

        complexity = ComplexityAnalyzer(self.graph).analyze()
        dependency = DependencyAnalyzer(self.graph).analyze(detect_cycles=True)
        metrics = MetricsAnalyzer(self.graph).analyze()

        # 清屏
        print("\033[2J\033[H", end="")

        # 渲染各部分
        self._render_header(metrics)
        print()
        self._render_overview(metrics)
        print()
        self._render_complexity_section(complexity)
        print()
        self._render_heatmap(complexity)
        print()
        self._render_dependency_section(dependency)
        print()
        self._render_top_functions(complexity)
        print()

        # 重置颜色
        print(Color.RESET)

    def _get_terminal_width(self) -> int:
        """获取终端宽度"""
        try:
            import shutil
            return shutil.get_terminal_size(fallback=(80, 24)).columns
        except Exception:
            return 80

    def _render_header(self, metrics: dict) -> None:
        """渲染标题区域"""
        w = self.width
        title = f"  CodeGraph-Lite: {self.project_name}"
        print(f"{Color.BRIGHT_CYAN}{Color.BOLD}{title}{Color.RESET}")
        print(f"{Color.DIM}{'─' * w}{Color.RESET}")

    def _render_overview(self, metrics: dict) -> None:
        """渲染项目概览"""
        print(f"{Color.BRIGHT_WHITE}{Color.BOLD}  [ 项目概览 ]{Color.RESET}")
        print()

        items = [
            ("文件数量", str(metrics["file_count"]), Color.BRIGHT_BLUE),
            ("函数数量", str(metrics["function_count"]), Color.BRIGHT_GREEN),
            ("类数量", str(metrics["class_count"]), Color.BRIGHT_MAGENTA),
            ("导入数量", str(metrics["import_count"]), Color.BRIGHT_YELLOW),
            ("变量数量", str(metrics["variable_count"]), Color.BRIGHT_CYAN),
            ("总代码行", str(metrics["total_loc"]), Color.BRIGHT_WHITE),
            ("平均复杂度", str(metrics["avg_function_complexity"]), Color.BRIGHT_RED),
        ]

        # 两列布局
        col_width = (self.width - 8) // 2
        for i in range(0, len(items), 2):
            left = items[i]
            right = items[i + 1] if i + 1 < len(items) else None

            line = f"    {Color.BRIGHT_WHITE}{left[0]}:{Color.RESET} {left[1]}"

            if right:
                padding = col_width - len(line) + len(Color.BRIGHT_WHITE) + len(Color.RESET)
                padding = max(padding, 4)
                line += " " * padding
                line += f"{Color.BRIGHT_WHITE}{right[0]}:{Color.RESET} {right[1]}"

            print(line)

        # 语言分布
        if metrics.get("files_by_language"):
            print()
            print(f"    {Color.DIM}语言分布:{Color.RESET}", end="")
            for lang, count in metrics["files_by_language"].items():
                print(f" {Color.BRIGHT_CYAN}{lang}{Color.RESET}({count})", end="")
            print()

    def _render_complexity_section(self, complexity: dict) -> None:
        """渲染复杂度分析区域"""
        print(f"{Color.BRIGHT_WHITE}{Color.BOLD}  [ 复杂度分析 ]{Color.RESET}")
        print()

        risk = complexity["risk_distribution"]
        total = complexity["total_functions"]

        print(f"    函数总数: {Color.BRIGHT_WHITE}{total}{Color.RESET}  "
              f"平均: {Color.BRIGHT_WHITE}{complexity['avg_complexity']}{Color.RESET}  "
              f"最大: {Color.BRIGHT_WHITE}{complexity['max_complexity']}{Color.RESET}")
        print()

        # 风险分布条形图
        bar_width = 40
        if total > 0:
            low_w = int(bar_width * risk["low"] / total)
            med_w = int(bar_width * risk["medium"] / total)
            high_w = int(bar_width * risk["high"] / total)
            crit_w = bar_width - low_w - med_w - high_w

            bar = (
                f"{Color.BG_BRIGHT_GREEN}{' ' * low_w}"
                f"{Color.BG_BRIGHT_YELLOW}{' ' * med_w}"
                f"{Color.BG_BRIGHT_RED}{' ' * high_w}"
                f"{Color.BG_RED}{' ' * max(crit_w, 0)}"
                f"{Color.RESET}"
            )
            print(f"    {bar}")
            print(f"    {Color.GREEN}低:{risk['low']}{Color.RESET}  "
                  f"{Color.YELLOW}中:{risk['medium']}{Color.RESET}  "
                  f"{Color.RED}高:{risk['high']}{Color.RESET}  "
                  f"{Color.BRIGHT_RED}极高:{risk['critical']}{Color.RESET}")

    def _render_heatmap(self, complexity: dict) -> None:
        """渲染复杂度热力图"""
        print(f"{Color.BRIGHT_WHITE}{Color.BOLD}  [ 复杂度热力图 ]{Color.RESET}")
        print(f"    {Color.DIM}每个方块代表一个函数，颜色越深复杂度越高{Color.RESET}")
        print()

        functions = complexity.get("functions", [])
        if not functions:
            print(f"    {Color.DIM}无函数数据{Color.RESET}")
            return

        # 渲染热力图方块
        cols = min(self.width - 8, 60)
        for i, func in enumerate(functions[:cols * 10]):
            c = func["complexity"]
            if c <= 2:
                bg = Color.BG_BRIGHT_GREEN
            elif c <= 5:
                bg = Color.BG_GREEN
            elif c <= 8:
                bg = Color.BG_BRIGHT_YELLOW
            elif c <= 12:
                bg = Color.BG_YELLOW
            elif c <= 18:
                bg = Color.BG_BRIGHT_RED
            else:
                bg = Color.BG_RED

            print(f"{bg} {Color.RESET}", end="")
            if (i + 1) % cols == 0:
                print()

        remaining = len(functions[:cols * 10]) % cols
        if remaining:
            print()

    def _render_dependency_section(self, dependency: dict) -> None:
        """渲染依赖关系区域"""
        print(f"{Color.BRIGHT_WHITE}{Color.BOLD}  [ 依赖关系 ]{Color.RESET}")
        print()

        print(f"    模块数量: {Color.BRIGHT_WHITE}{dependency['module_count']}{Color.RESET}  "
              f"依赖边数: {Color.BRIGHT_WHITE}{dependency['dependency_count']}{Color.RESET}  "
              f"最大深度: {Color.BRIGHT_WHITE}{dependency['max_depth']}{Color.RESET}")
        print()

        # 循环依赖
        if dependency["cycles"]:
            print(f"    {Color.BRIGHT_RED}{Color.BOLD}发现 {len(dependency['cycles'])} 个循环依赖:{Color.RESET}")
            for cycle in dependency["cycles"][:5]:
                path = f" {Color.BRIGHT_YELLOW}→{Color.RESET} ".join(cycle)
                print(f"    {Color.RED}⚠ {Color.RESET}{path}")
        else:
            print(f"    {Color.BRIGHT_GREEN}✓ 未发现循环依赖{Color.RESET}")

        # 依赖关系树（显示前10个模块）
        dep_tree = dependency.get("dependency_tree", {})
        if dep_tree:
            print()
            print(f"    {Color.DIM}依赖关系树 (部分):{Color.RESET}")
            shown = 0
            for module, deps in sorted(dep_tree.items()):
                if shown >= 10:
                    print(f"    {Color.DIM}... 还有 {len(dep_tree) - 10} 个模块{Color.RESET}")
                    break
                if deps:
                    print(f"    {Color.BRIGHT_CYAN}{module}{Color.RESET}")
                    for dep in sorted(deps)[:3]:
                        print(f"    {Color.DIM}├──{Color.RESET} {dep}")
                    if len(deps) > 3:
                        print(f"    {Color.DIM}└── ... ({len(deps) - 3} more){Color.RESET}")
                shown += 1

    def _render_top_functions(self, complexity: dict) -> None:
        """渲染 Top 10 最复杂函数"""
        print(f"{Color.BRIGHT_WHITE}{Color.BOLD}  [ Top 10 最复杂函数 ]{Color.RESET}")
        print()

        top_funcs = complexity["functions"][:10]
        if not top_funcs:
            print(f"    {Color.DIM}无函数数据{Color.RESET}")
            return

        max_name_len = max(len(f["name"]) for f in top_funcs)
        bar_max_width = self.width - max_name_len - 20

        for i, func in enumerate(top_funcs, 1):
            c = func["complexity"]
            name = func["name"]

            # 颜色根据复杂度变化
            if c <= 5:
                color = Color.GREEN
                bar_color = Color.BG_GREEN
            elif c <= 10:
                color = Color.YELLOW
                bar_color = Color.BG_YELLOW
            elif c <= 20:
                color = Color.BRIGHT_RED
                bar_color = Color.BG_BRIGHT_RED
            else:
                color = Color.RED
                bar_color = Color.BG_RED

            # 复杂度条
            bar_len = min(int(c * bar_max_width / max(top_funcs[0]["complexity"], 1)), bar_max_width)
            bar_len = max(bar_len, 1)
            bar = f"{bar_color}{' ' * bar_len}{Color.RESET}"

            # 行号
            fname = os.path.basename(func["file"])
            line_info = f"{Color.DIM}{fname}:{func['line']}{Color.RESET}"

            print(f"    {color}{i:>2}.{Color.RESET} "
                  f"{Color.BRIGHT_WHITE}{name:<{max_name_len}}{Color.RESET} "
                  f"{bar} "
                  f"{color}{c:>3}{Color.RESET} "
                  f"{line_info}")

        print()
        print(f"    {Color.DIM}{'─' * (self.width - 4)}{Color.RESET}")
        print(f"    {Color.DIM}Generated by CodeGraph-Lite v0.1.0{Color.RESET}")
