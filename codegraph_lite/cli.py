"""
CodeGraph-Lite 命令行参数解析模块

使用 argparse 实现子命令体系，支持 scan/report/dashboard/export/deps/complexity 命令。
"""

import argparse
import os
import sys
from typing import List, Optional


def _validate_path(path: str) -> str:
    """验证路径是否存在且是目录"""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"路径不存在: {path}")
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"不是有效的目录: {path}")
    return os.path.abspath(path)


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="codegraph",
        description="CodeGraph-Lite - 轻量级代码知识图谱智能分析引擎",
        epilog="示例: codegraph scan /path/to/project",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # scan 命令
    scan_parser = subparsers.add_parser(
        "scan", help="扫描项目，构建代码知识图谱"
    )
    scan_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )
    scan_parser.add_argument(
        "-l", "--language",
        type=str, default=None,
        help="指定语言 (python/javascript/go/rust/java)，默认自动检测",
    )
    scan_parser.add_argument(
        "--no-cache", action="store_true",
        help="禁用增量缓存",
    )
    scan_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="显示详细输出",
    )

    # report 命令
    report_parser = subparsers.add_parser(
        "report", help="生成项目分析报告"
    )
    report_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )
    report_parser.add_argument(
        "-o", "--output",
        type=str, default=None,
        help="输出文件路径（默认输出到终端）",
    )

    # dashboard 命令
    dash_parser = subparsers.add_parser(
        "dashboard", help="启动交互式TUI仪表盘"
    )
    dash_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )

    # export 命令
    export_parser = subparsers.add_parser(
        "export", help="导出图谱数据到指定格式"
    )
    export_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )
    export_parser.add_argument(
        "-f", "--format",
        type=str, choices=["json", "markdown", "html"], default="json",
        help="导出格式 (默认: json)",
    )
    export_parser.add_argument(
        "-o", "--output",
        type=str, default=None,
        help="输出文件路径（默认输出到终端）",
    )

    # deps 命令
    deps_parser = subparsers.add_parser(
        "deps", help="分析项目依赖关系"
    )
    deps_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )
    deps_parser.add_argument(
        "--detect-cycles", action="store_true", default=True,
        help="检测循环依赖（默认开启）",
    )

    # complexity 命令
    complexity_parser = subparsers.add_parser(
        "complexity", help="分析代码复杂度"
    )
    complexity_parser.add_argument(
        "path", type=_validate_path, help="项目根目录路径"
    )
    complexity_parser.add_argument(
        "-t", "--threshold",
        type=int, default=10,
        help="复杂度警告阈值（默认: 10）",
    )
    complexity_parser.add_argument(
        "--top", type=int, default=20,
        help="显示最复杂的N个函数（默认: 20）",
    )

    return parser


def _get_version() -> str:
    """获取版本号"""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数

    Args:
        argv: 命令行参数列表，为None时使用 sys.argv

    Returns:
        解析后的参数命名空间
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    return args


def run_command(args: argparse.Namespace) -> None:
    """执行对应的命令

    Args:
        args: 解析后的命令行参数
    """
    command = args.command

    if command == "scan":
        _cmd_scan(args)
    elif command == "report":
        _cmd_report(args)
    elif command == "dashboard":
        _cmd_dashboard(args)
    elif command == "export":
        _cmd_export(args)
    elif command == "deps":
        _cmd_deps(args)
    elif command == "complexity":
        _cmd_complexity(args)
    else:
        print(f"未知命令: {command}", file=sys.stderr)
        sys.exit(1)


def _cmd_scan(args: argparse.Namespace) -> None:
    """执行扫描命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker

    verbose = args.verbose
    no_cache = args.no_cache
    language = args.language
    project_path = args.path

    if verbose:
        print(f"[CodeGraph-Lite] 开始扫描项目: {project_path}")

    walker = FileWalker(project_path, language=language)
    files = walker.walk()

    if verbose:
        print(f"[CodeGraph-Lite] 发现 {len(files)} 个代码文件")

    builder = GraphBuilder(
        project_path=project_path,
        language=language,
        use_cache=not no_cache,
    )
    graph = builder.build(files)

    # 输出摘要
    node_counts = graph.count_nodes_by_type()
    edge_counts = graph.count_edges_by_type()

    print(f"\n{'='*60}")
    print(f"  CodeGraph-Lite 扫描结果")
    print(f"{'='*60}")
    print(f"  项目路径: {project_path}")
    print(f"  扫描文件: {len(files)}")
    print(f"  {'─'*56}")
    print(f"  节点统计:")
    for ntype, count in sorted(node_counts.items()):
        print(f"    {ntype}: {count}")
    print(f"  {'─'*56}")
    print(f"  边统计:")
    for etype, count in sorted(edge_counts.items()):
        print(f"    {etype}: {count}")
    print(f"{'='*60}\n")


def _cmd_report(args: argparse.Namespace) -> None:
    """执行报告命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker
    from .exporter.markdown_exporter import MarkdownExporter

    project_path = args.path

    walker = FileWalker(project_path)
    files = walker.walk()

    builder = GraphBuilder(project_path=project_path)
    graph = builder.build(files)

    exporter = MarkdownExporter()
    report = exporter.export(graph)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已生成: {args.output}")
    else:
        print(report)


def _cmd_dashboard(args: argparse.Namespace) -> None:
    """执行仪表盘命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker
    from .tui.dashboard import Dashboard

    project_path = args.path

    walker = FileWalker(project_path)
    files = walker.walk()

    builder = GraphBuilder(project_path=project_path)
    graph = builder.build(files)

    dashboard = Dashboard(graph, project_path)
    dashboard.render()


def _cmd_export(args: argparse.Namespace) -> None:
    """执行导出命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker

    project_path = args.path
    fmt = args.format

    walker = FileWalker(project_path)
    files = walker.walk()

    builder = GraphBuilder(project_path=project_path)
    graph = builder.build(files)

    if fmt == "json":
        from .exporter.json_exporter import JsonExporter
        exporter = JsonExporter()
    elif fmt == "markdown":
        from .exporter.markdown_exporter import MarkdownExporter
        exporter = MarkdownExporter()
    elif fmt == "html":
        from .exporter.html_exporter import HtmlExporter
        exporter = HtmlExporter()
    else:
        print(f"不支持的导出格式: {fmt}", file=sys.stderr)
        sys.exit(1)

    output = exporter.export(graph)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已导出到: {args.output}")
    else:
        print(output)


def _cmd_deps(args: argparse.Namespace) -> None:
    """执行依赖分析命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker
    from .analyzer.dependency import DependencyAnalyzer

    project_path = args.path

    walker = FileWalker(project_path)
    files = walker.walk()

    builder = GraphBuilder(project_path=project_path)
    graph = builder.build(files)

    analyzer = DependencyAnalyzer(graph)
    result = analyzer.analyze(detect_cycles=args.detect_cycles)

    print(f"\n{'='*60}")
    print(f"  依赖关系分析")
    print(f"{'='*60}")
    print(f"  项目路径: {project_path}")
    print(f"  模块数量: {result['module_count']}")
    print(f"  依赖边数: {result['dependency_count']}")
    print(f"  最大依赖深度: {result['max_depth']}")

    if result["cycles"]:
        print(f"\n  ⚠ 发现 {len(result['cycles'])} 个循环依赖:")
        for cycle in result["cycles"]:
            print(f"    {' -> '.join(cycle)}")
    else:
        print(f"\n  ✓ 未发现循环依赖")

    # 打印依赖树
    if result["dependency_tree"]:
        print(f"\n  依赖关系树:")
        for module, deps in sorted(result["dependency_tree"].items()):
            if deps:
                print(f"    {module}")
                for dep in sorted(deps):
                    print(f"      └── {dep}")

    print(f"{'='*60}\n")


def _cmd_complexity(args: argparse.Namespace) -> None:
    """执行复杂度分析命令"""
    from .graph.builder import GraphBuilder
    from .utils.file_walker import FileWalker
    from .analyzer.complexity import ComplexityAnalyzer

    project_path = args.path
    threshold = args.threshold
    top_n = args.top

    walker = FileWalker(project_path)
    files = walker.walk()

    builder = GraphBuilder(project_path=project_path)
    graph = builder.build(files)

    analyzer = ComplexityAnalyzer(graph)
    result = analyzer.analyze()

    print(f"\n{'='*60}")
    print(f"  代码复杂度分析")
    print(f"{'='*60}")
    print(f"  项目路径: {project_path}")
    print(f"  分析函数数: {result['total_functions']}")
    print(f"  平均复杂度: {result['avg_complexity']:.1f}")
    print(f"  最大复杂度: {result['max_complexity']}")
    print(f"  警告阈值: {threshold}")

    warnings = [f for f in result["functions"] if f["complexity"] > threshold]
    if warnings:
        print(f"\n  ⚠ 超过阈值的函数 ({len(warnings)} 个):")
        for func in sorted(warnings, key=lambda x: x["complexity"], reverse=True):
            print(f"    [{func['complexity']:>3}] {func['name']} ({func['file']})")
    else:
        print(f"\n  ✓ 所有函数复杂度均在阈值以下")

    print(f"\n  Top {top_n} 最复杂函数:")
    for func in result["functions"][:top_n]:
        bar_len = min(func["complexity"], 40)
        bar = "█" * bar_len
        print(f"    [{func['complexity']:>3}] {func['name']:<40} {bar}")

    print(f"{'='*60}\n")
