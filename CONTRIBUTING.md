# Contributing to CodeGraph-Lite

感谢你对 CodeGraph-Lite 的关注！欢迎贡献代码、报告问题或提出建议。

## 开发环境设置

```bash
# 克隆仓库
git clone <repo-url>
cd codegraph-lite

# 安装开发模式（无需额外依赖）
pip install -e .

# 运行测试
make test

# 代码格式检查
make lint
```

## 开发指南

### 项目结构

```
codegraph_lite/
├── parser/      # 多语言代码解析器
├── graph/       # 知识图谱构建
├── analyzer/    # 智能分析
├── exporter/    # 多格式导出
├── tui/         # TUI仪表盘
└── utils/       # 工具函数
```

### 添加新语言解析器

1. 在 `parser/` 目录下创建新的解析器文件（如 `cpp_parser.py`）
2. 继承 `BaseParser` 基类
3. 实现必要的方法：`parse_functions`, `parse_classes`, `parse_imports`, `parse_calls`
4. 在 `parser/__init__.py` 中注册新解析器

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写清晰的文档字符串
- 保持零外部依赖

### 提交规范

使用语义化提交信息：

```
feat: 添加C++语言解析器
fix: 修复循环依赖检测的边界情况
docs: 更新CLI使用文档
refactor: 重构图谱构建器
test: 添加解析器单元测试
```

## 报告问题

请使用 GitHub Issues 提交问题报告，包含以下信息：

- 操作系统和 Python 版本
- 复现步骤
- 期望行为和实际行为
- 如有错误信息，请附上完整的堆栈跟踪

## 许可证

通过向本项目贡献代码，你同意你的贡献将在 MIT 许可证下发布。
