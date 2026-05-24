<p align="center">
  <h1 align="center">🔍 CodeGraph Intelligence</h1>
  <p align="center">
    <strong>Lightweight Code Knowledge Graph Intelligent Analysis Engine</strong><br/>
    轻量级代码知识图谱智能分析引擎
  </p>
  <p align="center">
    <a href="#-简体中文">简体中文</a> ·
    <a href="#-繁體中文">繁體中文</a> ·
    <a href="#-english">English</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
    <img src="https://img.shields.io/badge/Dependencies-Zero-green.svg" alt="Zero Dependencies"/>
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/>
    <img src="https://img.shields.io/badge/Languages-6+-orange.svg" alt="Multi-Language"/>
  </p>
</p>

---

<a id="-简体中文"></a>

## 🎉 项目介绍

**CodeGraph Intelligence** 是一款轻量级代码知识图谱智能分析引擎，专为开发者打造的项目洞察工具。它能自动扫描代码仓库，构建完整的代码知识图谱，并提供智能化的分析报告。

### 💡 解决的痛点

- **代码理解困难**：面对陌生项目，难以快速理解代码结构和模块关系
- **AI上下文不足**：使用AI编码助手时，Token消耗大、上下文不完整
- **复杂度失控**：缺乏有效的代码复杂度监控手段
- **依赖混乱**：项目依赖关系不清晰，循环依赖难以发现

### 🌟 自研差异化亮点

- ✅ **零外部依赖**：纯Python标准库实现，无需安装任何第三方包
- ✅ **多语言支持**：支持Python、JavaScript/TypeScript、Go、Rust、Java及通用解析
- ✅ **交互式TUI**：精美的彩色终端仪表盘，实时可视化分析结果
- ✅ **增量缓存**：智能增量索引，大幅提升重复扫描速度
- ✅ **多格式导出**：JSON/Markdown/HTML三种格式，满足不同使用场景

---

## ✨ 核心特性

### 🔍 多语言代码解析
- **Python**：函数、类、导入、装饰器、异步函数
- **JavaScript/TypeScript**：function、箭头函数、class、import/require
- **Go**：func、struct、interface、goroutine
- **Rust**：fn、struct、enum、trait、impl、use
- **Java**：class、interface、enum、method、import
- **通用解析器**：基于文件扩展名的智能后备解析

### 🕸️ 知识图谱构建
- **5种节点类型**：Module（模块）、Class（类）、Function（函数）、Variable（变量）、Import（导入）
- **5种边类型**：CALLS（调用）、IMPORTS（导入）、INHERITS（继承）、CONTAINS（包含）、REFERENCES（引用）

### 📊 智能分析引擎
- **圈复杂度分析**：自动计算函数复杂度，标注风险等级（低/中/高/极高）
- **依赖关系分析**：构建模块依赖图，自动检测循环依赖
- **代码度量指标**：LOC、函数数量、类数量、平均复杂度、依赖深度

### 📤 多格式导出
- **JSON**：完整的图谱数据，方便程序化处理
- **Markdown**：结构化的分析报告，适合文档归档
- **HTML**：精美的可视化报告，深色主题，单文件可直接打开

### 🖥️ 交互式TUI仪表盘
- 项目概览面板（文件数、函数数、类数、总LOC）
- 复杂度热力图（彩色方块可视化）
- 依赖关系树状图
- Top 10 最复杂函数排行

---

## 🚀 快速开始

### 环境要求

- **Python** 3.8 或更高版本
- **操作系统**：Windows / macOS / Linux（跨平台兼容）
- **无其他依赖**：纯Python标准库，开箱即用

### 安装

```bash
# 方式一：从源码安装（推荐）
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install .

# 方式二：直接使用源码
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install -e .
```

### 基本使用

```bash
# 扫描项目，构建代码知识图谱
codegraph scan /path/to/your/project

# 生成项目分析报告
codegraph report /path/to/your/project

# 启动交互式TUI仪表盘
codegraph dashboard /path/to/your/project

# 导出图谱数据
codegraph export /path/to/your/project --format json
codegraph export /path/to/your/project --format markdown
codegraph export /path/to/your/project --format html

# 分析项目依赖关系
codegraph deps /path/to/your/project

# 分析代码复杂度
codegraph complexity /path/to/your/project
```

---

## 📖 详细使用指南

### 扫描项目

```bash
# 扫描当前目录
codegraph scan .

# 扫描指定路径
codegraph scan /path/to/project

# 排除特定目录
codegraph scan . --exclude node_modules,dist,build,.git
```

扫描完成后会输出：
- 扫描的文件数量
- 各类节点的统计（类、函数、导入、模块、变量）
- 各类边的统计（调用、包含、导入、继承）

### 生成报告

```bash
# 生成Markdown报告
codegraph report . --output report.md

# 生成HTML可视化报告
codegraph report . --format html --output report.html
```

### 导出数据

```bash
# 导出为JSON（方便程序化处理）
codegraph export . --format json --output graph.json

# 导出为Markdown（适合文档归档）
codegraph export . --format markdown --output graph.md

# 导出为HTML（精美可视化报告）
codegraph export . --format html --output graph.html
```

### 依赖分析

```bash
# 分析项目依赖关系
codegraph deps .

# 输出包括：
# - 模块依赖图
# - 循环依赖检测
# - 依赖深度分析
```

### 复杂度分析

```bash
# 分析代码复杂度
codegraph complexity .

# 输出包括：
# - 各函数圈复杂度
# - 风险等级分布
# - Top N 最复杂函数
```

### TUI仪表盘

```bash
# 启动交互式终端仪表盘
codegraph dashboard .
```

仪表盘包含：
- 📈 项目概览统计
- 🎨 复杂度热力图
- 🌳 依赖关系树
- 📊 Top 10 复杂度排行

---

## 💡 设计思路与迭代规划

### 设计理念

CodeGraph Intelligence 的设计遵循以下核心理念：

1. **零依赖哲学**：不引入任何第三方库，确保在任何Python环境下都能运行
2. **正则驱动**：使用正则表达式进行代码解析，轻量高效，避免AST解析的复杂性
3. **增量优先**：通过文件哈希缓存机制，只重新解析变更的文件
4. **可视化驱动**：TUI仪表盘和HTML报告让分析结果一目了然

### 技术选型

| 组件 | 技术方案 | 选型原因 |
|------|---------|---------|
| 代码解析 | 正则表达式 | 轻量、跨语言、无依赖 |
| 图谱存储 | 内存字典 | 简单高效，支持快速查询 |
| 缓存机制 | JSON文件 | 人类可读，便于调试 |
| TUI渲染 | ANSI转义码 | 标准库支持，跨平台 |
| HTML报告 | 内联CSS | 单文件，无外部依赖 |

### 后续迭代计划

- [ ] 🔮 支持更多编程语言（C/C++、Ruby、PHP、Kotlin等）
- [ ] 📊 增加代码变更趋势分析
- [ ] 🔄 支持Git历史分析，追踪代码演进
- [ ] 🌐 Web界面版本
- [ ] 🔌 插件系统，支持自定义分析规则
- [ ] 📈 集成CI/CD，自动化代码质量检查

---

## 📦 打包与部署指南

### 作为Python包安装

```bash
# 安装到系统
pip install .

# 开发模式安装（可编辑）
pip install -e .
```

### 使用Makefile

```bash
# 安装
make install

# 运行测试
make test

# 生成报告
make report

# 清理缓存
make clean
```

### 直接运行

```bash
# 无需安装，直接运行
python -m codegraph_lite scan /path/to/project
```

### 兼容环境

| 环境 | 支持状态 |
|------|---------|
| Python 3.8+ | ✅ 完全支持 |
| Windows | ✅ 完全支持 |
| macOS | ✅ 完全支持 |
| Linux | ✅ 完全支持 |
| WSL | ✅ 完全支持 |

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是Bug报告、功能建议还是代码提交。

### 提交规范

请遵循 [Angular Commit Convention](https://conventionalcommits.org/)：

```
feat: 新增功能
fix: 修复问题
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具变更
```

### 提交流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### Issue反馈

请使用 [GitHub Issues](https://github.com/gitstq/CodeGraph-Intelligence/issues) 提交Bug报告或功能建议，提交时请附上：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 运行环境信息

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2026 CodeGraph Intelligence Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<a id="-繁體中文"></a>

## 🎉 專案介紹

**CodeGraph Intelligence** 是一款輕量級程式碼知識圖譜智慧分析引擎，專為開發者打造的專案洞察工具。它能自動掃描程式碼倉庫，建構完整的程式碼知識圖譜，並提供智慧化的分析報告。

### 💡 解決的痛點

- **程式碼理解困難**：面對陌生專案，難以快速理解程式碼結構和模組關係
- **AI上下文不足**：使用AI編碼助手時，Token消耗大、上下文不完整
- **複雜度失控**：缺乏有效的程式碼複雜度監控手段
- **依賴混亂**：專案依賴關係不清晰，循環依賴難以發現

### 🌟 自研差異化亮點

- ✅ **零外部依賴**：純Python標準庫實現，無需安裝任何第三方套件
- ✅ **多語言支援**：支援Python、JavaScript/TypeScript、Go、Rust、Java及通用解析
- ✅ **互動式TUI**：精美的彩色終端儀表盤，即時視覺化分析結果
- ✅ **增量快取**：智慧增量索引，大幅提升重複掃描速度
- ✅ **多格式匯出**：JSON/Markdown/HTML三種格式，滿足不同使用場景

---

## ✨ 核心特性

### 🔍 多語言程式碼解析
- **Python**：函式、類別、匯入、裝飾器、非同步函式
- **JavaScript/TypeScript**：function、箭頭函式、class、import/require
- **Go**：func、struct、interface、goroutine
- **Rust**：fn、struct、enum、trait、impl、use
- **Java**：class、interface、enum、method、import
- **通用解析器**：基於副檔名的智慧後備解析

### 🕸️ 知識圖譜建構
- **5種節點類型**：Module（模組）、Class（類別）、Function（函式）、Variable（變數）、Import（匯入）
- **5種邊類型**：CALLS（呼叫）、IMPORTS（匯入）、INHERITS（繼承）、CONTAINS（包含）、REFERENCES（引用）

### 📊 智慧分析引擎
- **圈複雜度分析**：自動計算函式複雜度，標註風險等級（低/中/高/極高）
- **依賴關係分析**：建構模組依賴圖，自動偵測循環依賴
- **程式碼度量指標**：LOC、函式數量、類別數量、平均複雜度、依賴深度

### 📤 多格式匯出
- **JSON**：完整的圖譜資料，方便程式化處理
- **Markdown**：結構化的分析報告，適合文件歸檔
- **HTML**：精美的視覺化報告，深色主題，單檔案可直接開啟

### 🖥️ 互動式TUI儀表盤
- 專案概覽面板（檔案數、函式數、類別數、總LOC）
- 複雜度熱力圖（彩色方塊視覺化）
- 依賴關係樹狀圖
- Top 10 最複雜函式排行

---

## 🚀 快速開始

### 環境要求

- **Python** 3.8 或更高版本
- **作業系統**：Windows / macOS / Linux（跨平台相容）
- **無其他依賴**：純Python標準庫，開箱即用

### 安裝

```bash
# 方式一：從原始碼安裝（推薦）
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install .

# 方式二：直接使用原始碼
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install -e .
```

### 基本使用

```bash
# 掃描專案，建構程式碼知識圖譜
codegraph scan /path/to/your/project

# 產生專案分析報告
codegraph report /path/to/your/project

# 啟動互動式TUI儀表盤
codegraph dashboard /path/to/your/project

# 匯出圖譜資料
codegraph export /path/to/your/project --format json
codegraph export /path/to/your/project --format markdown
codegraph export /path/to/your/project --format html

# 分析專案依賴關係
codegraph deps /path/to/your/project

# 分析程式碼複雜度
codegraph complexity /path/to/your/project
```

---

## 📖 詳細使用指南

### 掃描專案

```bash
# 掃描目前目錄
codegraph scan .

# 掃描指定路徑
codegraph scan /path/to/project

# 排除特定目錄
codegraph scan . --exclude node_modules,dist,build,.git
```

掃描完成後會輸出：
- 掃描的檔案數量
- 各類節點的統計（類別、函式、匯入、模組、變數）
- 各類邊的統計（呼叫、包含、匯入、繼承）

### 產生報告

```bash
# 產生Markdown報告
codegraph report . --output report.md

# 產生HTML視覺化報告
codegraph report . --format html --output report.html
```

### 匯出資料

```bash
# 匯出為JSON（方便程式化處理）
codegraph export . --format json --output graph.json

# 匯出為Markdown（適合文件歸檔）
codegraph export . --format markdown --output graph.md

# 匯出為HTML（精美視覺化報告）
codegraph export . --format html --output graph.html
```

### 依賴分析

```bash
# 分析專案依賴關係
codegraph deps .

# 輸出包括：
# - 模組依賴圖
# - 循環依賴偵測
# - 依賴深度分析
```

### 複雜度分析

```bash
# 分析程式碼複雜度
codegraph complexity .

# 輸出包括：
# - 各函式圈複雜度
# - 風險等級分佈
# - Top N 最複雜函式
```

### TUI儀表盤

```bash
# 啟動互動式終端儀表盤
codegraph dashboard .
```

儀表盤包含：
- 📈 專案概覽統計
- 🎨 複雜度熱力圖
- 🌳 依賴關係樹
- 📊 Top 10 複雜度排行

---

## 💡 設計思路與迭代規劃

### 設計理念

CodeGraph Intelligence 的設計遵循以下核心理念：

1. **零依賴哲學**：不引入任何第三方函式庫，確保在任何Python環境下都能運行
2. **正則驅動**：使用正規表達式進行程式碼解析，輕量高效，避免AST解析的複雜性
3. **增量優先**：透過檔案雜湊快取機制，只重新解析變更的檔案
4. **視覺化驅動**：TUI儀表盤和HTML報告讓分析結果一目了然

### 技術選型

| 元件 | 技術方案 | 選型原因 |
|------|---------|---------|
| 程式碼解析 | 正規表達式 | 輕量、跨語言、無依賴 |
| 圖譜儲存 | 記憶體字典 | 簡單高效，支援快速查詢 |
| 快取機制 | JSON檔案 | 人類可讀，便於除錯 |
| TUI渲染 | ANSI轉義碼 | 標準庫支援，跨平台 |
| HTML報告 | 內聯CSS | 單檔案，無外部依賴 |

### 後續迭代計劃

- [ ] 🔮 支援更多程式語言（C/C++、Ruby、PHP、Kotlin等）
- [ ] 📊 增加程式碼變更趨勢分析
- [ ] 🔄 支援Git歷史分析，追蹤程式碼演進
- [ ] 🌐 Web介面版本
- [ ] 🔌 外掛系統，支援自訂分析規則
- [ ] 📈 整合CI/CD，自動化程式碼品質檢查

---

## 📦 打包與部署指南

### 作為Python套件安裝

```bash
# 安裝到系統
pip install .

# 開發模式安裝（可編輯）
pip install -e .
```

### 使用Makefile

```bash
# 安裝
make install

# 執行測試
make test

# 產生報告
make report

# 清理快取
make clean
```

### 直接執行

```bash
# 無需安裝，直接執行
python -m codegraph_lite scan /path/to/project
```

### 相容環境

| 環境 | 支援狀態 |
|------|---------|
| Python 3.8+ | ✅ 完全支援 |
| Windows | ✅ 完全支援 |
| macOS | ✅ 完全支援 |
| Linux | ✅ 完全支援 |
| WSL | ✅ 完全支援 |

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！無論是Bug回報、功能建議還是程式碼提交。

### 提交規範

請遵循 [Angular Commit Convention](https://conventionalcommits.org/)：

```
feat: 新增功能
fix: 修復問題
docs: 文件更新
refactor: 程式碼重構
test: 測試相關
chore: 建構/工具變更
```

### 提交流程

1. Fork 本倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: 新增某個功能'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

### Issue回饋

請使用 [GitHub Issues](https://github.com/gitstq/CodeGraph-Intelligence/issues) 提交Bug回報或功能建議，提交時請附上：
- 問題描述
- 重現步驟
- 期望行為
- 實際行為
- 執行環境資訊

---

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<a id="-english"></a>

## 🎉 Introduction

**CodeGraph Intelligence** is a lightweight code knowledge graph intelligent analysis engine designed for developers. It automatically scans code repositories, builds comprehensive code knowledge graphs, and provides intelligent analysis reports.

### 💡 Problems We Solve

- **Code comprehension difficulty**: Hard to quickly understand code structure and module relationships in unfamiliar projects
- **Insufficient AI context**: High token consumption and incomplete context when using AI coding assistants
- **Complexity management**: Lack of effective code complexity monitoring tools
- **Dependency chaos**: Unclear project dependency relationships, hard-to-detect circular dependencies

### 🌟 Differentiation Highlights

- ✅ **Zero Dependencies**: Built entirely with Python standard library, no third-party packages needed
- ✅ **Multi-Language Support**: Python, JavaScript/TypeScript, Go, Rust, Java, and generic parsing
- ✅ **Interactive TUI**: Beautiful colored terminal dashboard with real-time visualization
- ✅ **Incremental Caching**: Smart incremental indexing for significantly faster repeated scans
- ✅ **Multi-Format Export**: JSON/Markdown/HTML formats for different use cases

---

## ✨ Core Features

### 🔍 Multi-Language Code Parsing
- **Python**: Functions, classes, imports, decorators, async functions
- **JavaScript/TypeScript**: function, arrow functions, class, import/require
- **Go**: func, struct, interface, goroutine
- **Rust**: fn, struct, enum, trait, impl, use
- **Java**: class, interface, enum, method, import
- **Generic Parser**: Intelligent fallback parsing based on file extensions

### 🕸️ Knowledge Graph Construction
- **5 Node Types**: Module, Class, Function, Variable, Import
- **5 Edge Types**: CALLS, IMPORTS, INHERITS, CONTAINS, REFERENCES

### 📊 Intelligent Analysis Engine
- **Cyclomatic Complexity**: Automatic function complexity calculation with risk level classification (Low/Medium/High/Critical)
- **Dependency Analysis**: Module dependency graph with circular dependency detection
- **Code Metrics**: LOC, function count, class count, average complexity, dependency depth

### 📤 Multi-Format Export
- **JSON**: Complete graph data for programmatic processing
- **Markdown**: Structured analysis reports for documentation
- **HTML**: Beautiful visualization reports with dark theme, single-file output

### 🖥️ Interactive TUI Dashboard
- Project overview panel (file count, function count, class count, total LOC)
- Complexity heatmap (color-coded visualization)
- Dependency tree view
- Top 10 most complex functions ranking

---

## 🚀 Quick Start

### Requirements

- **Python** 3.8 or higher
- **OS**: Windows / macOS / Linux (cross-platform)
- **No other dependencies**: Pure Python standard library, ready to use

### Installation

```bash
# Option 1: Install from source (Recommended)
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install .

# Option 2: Editable install
git clone https://github.com/gitstq/CodeGraph-Intelligence.git
cd CodeGraph-Intelligence
pip install -e .
```

### Basic Usage

```bash
# Scan project and build code knowledge graph
codegraph scan /path/to/your/project

# Generate project analysis report
codegraph report /path/to/your/project

# Launch interactive TUI dashboard
codegraph dashboard /path/to/your/project

# Export graph data
codegraph export /path/to/your/project --format json
codegraph export /path/to/your/project --format markdown
codegraph export /path/to/your/project --format html

# Analyze project dependencies
codegraph deps /path/to/your/project

# Analyze code complexity
codegraph complexity /path/to/your/project
```

---

## 📖 Detailed Usage Guide

### Scanning Projects

```bash
# Scan current directory
codegraph scan .

# Scan specific path
codegraph scan /path/to/project

# Exclude specific directories
codegraph scan . --exclude node_modules,dist,build,.git
```

Output includes:
- Number of scanned files
- Node statistics (classes, functions, imports, modules, variables)
- Edge statistics (calls, contains, imports, inherits)

### Generating Reports

```bash
# Generate Markdown report
codegraph report . --output report.md

# Generate HTML visualization report
codegraph report . --format html --output report.html
```

### Exporting Data

```bash
# Export as JSON
codegraph export . --format json --output graph.json

# Export as Markdown
codegraph export . --format markdown --output graph.md

# Export as HTML
codegraph export . --format html --output graph.html
```

### Dependency Analysis

```bash
# Analyze project dependencies
codegraph deps .

# Output includes:
# - Module dependency graph
# - Circular dependency detection
# - Dependency depth analysis
```

### Complexity Analysis

```bash
# Analyze code complexity
codegraph complexity .

# Output includes:
# - Cyclomatic complexity per function
# - Risk level distribution
# - Top N most complex functions
```

### TUI Dashboard

```bash
# Launch interactive terminal dashboard
codegraph dashboard .
```

Dashboard includes:
- 📈 Project overview statistics
- 🎨 Complexity heatmap
- 🌳 Dependency tree
- 📊 Top 10 complexity ranking

---

## 💡 Design Philosophy & Roadmap

### Design Principles

1. **Zero Dependency Philosophy**: No third-party libraries, runs in any Python environment
2. **Regex-Driven**: Uses regular expressions for code parsing — lightweight, cross-language, dependency-free
3. **Incremental First**: File hash caching mechanism to only re-parse changed files
4. **Visualization-Driven**: TUI dashboard and HTML reports make analysis results clear at a glance

### Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Code Parsing | Regular Expressions | Lightweight, cross-language, no dependencies |
| Graph Storage | In-memory Dict | Simple, efficient, fast queries |
| Caching | JSON Files | Human-readable, easy to debug |
| TUI Rendering | ANSI Escape Codes | Standard library support, cross-platform |
| HTML Reports | Inline CSS | Single file, no external dependencies |

### Roadmap

- [ ] 🔮 Support more languages (C/C++, Ruby, PHP, Kotlin, etc.)
- [ ] 📊 Code change trend analysis
- [ ] 🔄 Git history analysis for code evolution tracking
- [ ] 🌐 Web interface version
- [ ] 🔌 Plugin system for custom analysis rules
- [ ] 📈 CI/CD integration for automated code quality checks

---

## 📦 Packaging & Deployment

### Install as Python Package

```bash
# System install
pip install .

# Editable install
pip install -e .
```

### Using Makefile

```bash
# Install
make install

# Run tests
make test

# Generate report
make report

# Clean cache
make clean
```

### Run Directly

```bash
# No installation needed
python -m codegraph_lite scan /path/to/project
```

### Compatible Environments

| Environment | Status |
|------------|--------|
| Python 3.8+ | ✅ Fully Supported |
| Windows | ✅ Fully Supported |
| macOS | ✅ Fully Supported |
| Linux | ✅ Fully Supported |
| WSL | ✅ Fully Supported |

---

## 🤝 Contributing

We welcome all forms of contribution! Whether it's bug reports, feature suggestions, or code submissions.

### Commit Convention

Please follow [Angular Commit Convention](https://conventionalcommits.org/):

```
feat: new feature
fix: bug fix
docs: documentation update
refactor: code refactoring
test: test related
chore: build/tooling changes
```

### Contribution Workflow

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add some feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Issue Reporting

Please use [GitHub Issues](https://github.com/gitstq/CodeGraph-Intelligence/issues) to submit bug reports or feature suggestions. Include:
- Problem description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Runtime environment information

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
