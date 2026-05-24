"""
HTML 格式导出器

将代码知识图谱导出为带CSS样式的可视化HTML报告（单文件，内联CSS）。
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph.builder import CodeGraph


class HtmlExporter:
    """HTML 格式导出器

    将代码知识图谱导出为美观的单文件 HTML 报告。
    所有 CSS 样式内联，无需外部依赖。
    """

    def export(self, graph: "CodeGraph") -> str:
        """导出为 HTML 字符串

        Args:
            graph: 代码知识图谱

        Returns:
            HTML 格式的字符串
        """
        from ..analyzer.complexity import ComplexityAnalyzer
        from ..analyzer.dependency import DependencyAnalyzer
        from ..analyzer.metrics import MetricsAnalyzer

        complexity = ComplexityAnalyzer(graph).analyze()
        dependency = DependencyAnalyzer(graph).analyze(detect_cycles=True)
        metrics = MetricsAnalyzer(graph).analyze()

        project_name = os.path.basename(graph.project_path) or "Project"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeGraph-Lite - {project_name}</title>
<style>
{self._get_css()}
</style>
</head>
<body>
<div class="container">
{self._render_header(project_name, metrics)}
{self._render_overview(metrics)}
{self._render_language_distribution(metrics)}
{self._render_complexity(complexity)}
{self._render_complexity_heatmap(complexity)}
{self._render_dependency(dependency)}
{self._render_top_functions(complexity)}
{self._render_file_details(metrics)}
</div>
<script>
{self._get_js()}
</script>
</body>
</html>"""

        return html

    def _get_css(self) -> str:
        """获取内联CSS样式"""
        return """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #0f1117;
    color: #e1e4e8;
    line-height: 1.6;
    padding: 20px;
}
.container { max-width: 1200px; margin: 0 auto; }
.header {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #1a1e2e 0%, #2d1b4e 100%);
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid #30363d;
}
.header h1 {
    font-size: 2.5em;
    background: linear-gradient(90deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.header p { color: #8b949e; font-size: 1.1em; }
.section {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
}
.section h2 {
    font-size: 1.4em;
    color: #58a6ff;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #21262d;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}
.stat-card {
    background: #21262d;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    border: 1px solid #30363d;
    transition: transform 0.2s, border-color 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    border-color: #58a6ff;
}
.stat-card .value {
    font-size: 2em;
    font-weight: 700;
    color: #58a6ff;
}
.stat-card .label {
    font-size: 0.85em;
    color: #8b949e;
    margin-top: 4px;
}
.bar-chart { margin-top: 16px; }
.bar-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}
.bar-label {
    width: 120px;
    font-size: 0.9em;
    color: #8b949e;
    text-align: right;
    padding-right: 12px;
    flex-shrink: 0;
}
.bar-track {
    flex: 1;
    height: 24px;
    background: #21262d;
    border-radius: 4px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}
.bar-fill.blue { background: linear-gradient(90deg, #1f6feb, #58a6ff); }
.bar-fill.green { background: linear-gradient(90deg, #238636, #3fb950); }
.bar-fill.purple { background: linear-gradient(90deg, #8957e5, #bc8cff); }
.bar-fill.orange { background: linear-gradient(90deg, #d29922, #e3b341); }
.bar-fill.red { background: linear-gradient(90deg, #da3633, #f85149); }
.bar-value {
    width: 60px;
    text-align: right;
    font-size: 0.9em;
    color: #e1e4e8;
    padding-left: 8px;
    flex-shrink: 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
}
th {
    text-align: left;
    padding: 10px 12px;
    background: #21262d;
    color: #8b949e;
    font-weight: 600;
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #30363d;
}
td {
    padding: 10px 12px;
    border-bottom: 1px solid #21262d;
    font-size: 0.9em;
}
tr:hover td { background: #1c2129; }
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
}
.badge-low { background: #0d2818; color: #3fb950; }
.badge-medium { background: #2a1f00; color: #e3b341; }
.badge-high { background: #3d1200; color: #f0883e; }
.badge-critical { background: #3d0a0a; color: #f85149; }
.heatmap {
    display: flex;
    flex-wrap: wrap;
    gap: 3px;
    margin-top: 12px;
}
.heat-cell {
    width: 16px;
    height: 16px;
    border-radius: 2px;
    transition: transform 0.15s;
}
.heat-cell:hover { transform: scale(1.5); z-index: 1; position: relative; }
.heat-1 { background: #0d2818; }
.heat-2 { background: #163b27; }
.heat-3 { background: #238636; }
.heat-4 { background: #2ea043; }
.heat-5 { background: #e3b341; }
.heat-6 { background: #d29922; }
.heat-7 { background: #f0883e; }
.heat-8 { background: #da3633; }
.heat-9 { background: #f85149; }
.cycle-warning {
    background: #3d1200;
    border: 1px solid #f0883e;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    color: #f0883e;
    font-size: 0.9em;
}
.no-cycles {
    background: #0d2818;
    border: 1px solid #3fb950;
    border-radius: 8px;
    padding: 12px 16px;
    color: #3fb950;
    font-size: 0.9em;
}
.legend {
    display: flex;
    gap: 16px;
    margin-top: 12px;
    flex-wrap: wrap;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85em;
    color: #8b949e;
}
.legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}
.footer {
    text-align: center;
    padding: 20px;
    color: #484f58;
    font-size: 0.85em;
}
"""

    def _get_js(self) -> str:
        """获取内联JavaScript"""
        return """
// 简单的交互效果
document.addEventListener('DOMContentLoaded', function() {
    // 热力图单元格提示
    var cells = document.querySelectorAll('.heat-cell');
    cells.forEach(function(cell) {
        cell.addEventListener('mouseenter', function() {
            this.title = this.getAttribute('data-info') || '';
        });
    });
});
"""

    def _render_header(self, project_name: str, metrics: dict) -> str:
        """渲染页面头部"""
        return f"""
    <div class="header">
        <h1>CodeGraph-Lite</h1>
        <p>{project_name} - 代码知识图谱分析报告</p>
    </div>"""

    def _render_overview(self, metrics: dict) -> str:
        """渲染项目概览"""
        return f"""
    <div class="section">
        <h2>项目概览</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{metrics['file_count']}</div>
                <div class="label">文件数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{metrics['function_count']}</div>
                <div class="label">函数数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{metrics['class_count']}</div>
                <div class="label">类数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{metrics['import_count']}</div>
                <div class="label">导入数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{metrics['total_loc']}</div>
                <div class="label">总代码行数</div>
            </div>
            <div class="stat-card">
                <div class="value">{metrics['avg_function_complexity']}</div>
                <div class="label">平均复杂度</div>
            </div>
        </div>
    </div>"""

    def _render_language_distribution(self, metrics: dict) -> str:
        """渲染语言分布"""
        if not metrics.get("files_by_language"):
            return ""

        lang_data = metrics["files_by_language"]
        max_count = max(lang_data.values()) if lang_data else 1

        bars = ""
        colors = ["blue", "green", "purple", "orange", "red"]
        for i, (lang, count) in enumerate(lang_data.items()):
            pct = (count / max_count) * 100
            color = colors[i % len(colors)]
            bars += f"""
            <div class="bar-item">
                <div class="bar-label">{lang}</div>
                <div class="bar-track">
                    <div class="bar-fill {color}" style="width: {pct}%"></div>
                </div>
                <div class="bar-value">{count}</div>
            </div>"""

        return f"""
    <div class="section">
        <h2>语言分布</h2>
        <div class="bar-chart">{bars}</div>
    </div>"""

    def _render_complexity(self, complexity: dict) -> str:
        """渲染复杂度分析"""
        risk = complexity["risk_distribution"]

        return f"""
    <div class="section">
        <h2>复杂度分析</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{complexity['total_functions']}</div>
                <div class="label">函数总数</div>
            </div>
            <div class="stat-card">
                <div class="value">{complexity['avg_complexity']}</div>
                <div class="label">平均复杂度</div>
            </div>
            <div class="stat-card">
                <div class="value">{complexity['max_complexity']}</div>
                <div class="label">最大复杂度</div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <h3 style="color: #8b949e; margin-bottom: 12px;">风险等级分布</h3>
            <div class="stats-grid" style="grid-template-columns: repeat(4, 1fr);">
                <div class="stat-card">
                    <div class="value" style="color: #3fb950;">{risk['low']}</div>
                    <div class="label"><span class="badge badge-low">低风险</span> 1-5</div>
                </div>
                <div class="stat-card">
                    <div class="value" style="color: #e3b341;">{risk['medium']}</div>
                    <div class="label"><span class="badge badge-medium">中风险</span> 6-10</div>
                </div>
                <div class="stat-card">
                    <div class="value" style="color: #f0883e;">{risk['high']}</div>
                    <div class="label"><span class="badge badge-high">高风险</span> 11-20</div>
                </div>
                <div class="stat-card">
                    <div class="value" style="color: #f85149;">{risk['critical']}</div>
                    <div class="label"><span class="badge badge-critical">极高</span> &gt;20</div>
                </div>
            </div>
        </div>
    </div>"""

    def _render_complexity_heatmap(self, complexity: dict) -> str:
        """渲染复杂度热力图"""
        functions = complexity.get("functions", [])
        if not functions:
            return ""

        cells = ""
        for func in functions[:200]:  # 最多显示200个
            c = func["complexity"]
            if c <= 2:
                heat = "heat-1"
            elif c <= 4:
                heat = "heat-2"
            elif c <= 6:
                heat = "heat-3"
            elif c <= 8:
                heat = "heat-4"
            elif c <= 10:
                heat = "heat-5"
            elif c <= 15:
                heat = "heat-6"
            elif c <= 20:
                heat = "heat-7"
            elif c <= 30:
                heat = "heat-8"
            else:
                heat = "heat-9"

            fname = os.path.basename(func["file"])
            cells += f'<div class="heat-cell {heat}" data-info="{func["name"]} ({fname}:{func["line"]}) - 复杂度: {c}"></div>'

        return f"""
    <div class="section">
        <h2>复杂度热力图</h2>
        <p style="color: #8b949e; font-size: 0.9em; margin-bottom: 12px;">
            每个方块代表一个函数，颜色越深表示复杂度越高
        </p>
        <div class="heatmap">{cells}</div>
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #0d2818;"></div> 1-2</div>
            <div class="legend-item"><div class="legend-color" style="background: #163b27;"></div> 3-4</div>
            <div class="legend-item"><div class="legend-color" style="background: #238636;"></div> 5-6</div>
            <div class="legend-item"><div class="legend-color" style="background: #2ea043;"></div> 7-8</div>
            <div class="legend-item"><div class="legend-color" style="background: #e3b341;"></div> 9-10</div>
            <div class="legend-item"><div class="legend-color" style="background: #d29922;"></div> 11-15</div>
            <div class="legend-item"><div class="legend-color" style="background: #f0883e;"></div> 16-20</div>
            <div class="legend-item"><div class="legend-color" style="background: #da3633;"></div> 21-30</div>
            <div class="legend-item"><div class="legend-color" style="background: #f85149;"></div> &gt;30</div>
        </div>
    </div>"""

    def _render_dependency(self, dependency: dict) -> str:
        """渲染依赖分析"""
        cycles_html = ""
        if dependency["cycles"]:
            for cycle in dependency["cycles"]:
                cycle_str = " &rarr; ".join(cycle)
                cycles_html += f'<div class="cycle-warning">&#9888; {cycle_str}</div>'
        else:
            cycles_html = '<div class="no-cycles">&#10003; 未检测到循环依赖</div>'

        # 被依赖最多的模块
        dep_table = ""
        if dependency["most_depended"]:
            rows = ""
            for item in dependency["most_depended"]:
                rows += f"""
                <tr>
                    <td><code>{item['module']}</code></td>
                    <td>{item['count']}</td>
                </tr>"""
            dep_table = f"""
            <div style="margin-top: 20px;">
                <h3 style="color: #8b949e; margin-bottom: 12px;">被依赖最多的模块</h3>
                <table>
                    <thead><tr><th>模块</th><th>被依赖次数</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>"""

        return f"""
    <div class="section">
        <h2>依赖分析</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{dependency['module_count']}</div>
                <div class="label">模块数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{dependency['dependency_count']}</div>
                <div class="label">依赖边数</div>
            </div>
            <div class="stat-card">
                <div class="value">{dependency['max_depth']}</div>
                <div class="label">最大依赖深度</div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <h3 style="color: #8b949e; margin-bottom: 12px;">循环依赖检测</h3>
            {cycles_html}
        </div>
        {dep_table}
    </div>"""

    def _render_top_functions(self, complexity: dict) -> str:
        """渲染Top复杂函数"""
        top_funcs = complexity["functions"][:15]
        if not top_funcs:
            return ""

        rows = ""
        for i, func in enumerate(top_funcs, 1):
            c = func["complexity"]
            if c <= 5:
                badge = "badge-low"
                label = "低"
            elif c <= 10:
                badge = "badge-medium"
                label = "中"
            elif c <= 20:
                badge = "badge-high"
                label = "高"
            else:
                badge = "badge-critical"
                label = "极高"

            fname = os.path.basename(func["file"])
            rows += f"""
            <tr>
                <td>#{i}</td>
                <td><code>{func['name']}</code></td>
                <td><span class="badge {badge}">{c} ({label})</span></td>
                <td>{fname}</td>
                <td>{func['line']}</td>
            </tr>"""

        return f"""
    <div class="section">
        <h2>Top 15 最复杂函数</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>函数名</th>
                    <th>复杂度</th>
                    <th>文件</th>
                    <th>行号</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""

    def _render_file_details(self, metrics: dict) -> str:
        """渲染文件详情表格"""
        file_stats = metrics.get("file_stats", {})
        if not file_stats:
            return ""

        rows = ""
        for file_path, stats in sorted(
            file_stats.items(), key=lambda x: x[1]["loc"], reverse=True
        )[:30]:
            fname = os.path.basename(file_path)
            rows += f"""
            <tr>
                <td><code>{fname}</code></td>
                <td>{stats['loc']}</td>
                <td>{stats['function_count']}</td>
                <td>{stats['class_count']}</td>
                <td>{stats['import_count']}</td>
            </tr>"""

        return f"""
    <div class="section">
        <h2>文件详情 (Top 30)</h2>
        <table>
            <thead>
                <tr>
                    <th>文件</th>
                    <th>LOC</th>
                    <th>函数</th>
                    <th>类</th>
                    <th>导入</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    <div class="footer">
        <p>Generated by CodeGraph-Lite v0.1.0</p>
    </div>"""
