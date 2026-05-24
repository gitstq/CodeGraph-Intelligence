"""
文件遍历模块

递归遍历项目目录，按语言过滤代码文件。
"""

import os
from typing import List, Optional, Set


# 支持的代码文件扩展名
DEFAULT_EXTENSIONS: Set[str] = {
    # Python
    ".py",
    # JavaScript / TypeScript
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Go
    ".go",
    # Rust
    ".rs",
    # Java
    ".java",
    # C/C++
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    # C#
    ".cs",
    # Ruby
    ".rb",
    # PHP
    ".php",
    # Swift
    ".swift",
    # Kotlin
    ".kt", ".kts",
    # Scala
    ".scala",
    # Shell
    ".sh", ".bash", ".zsh",
    # Lua
    ".lua",
    # R
    ".r", ".R",
    # Dart
    ".dart",
}

# 语言 -> 扩展名映射
LANGUAGE_EXTENSIONS: dict = {
    "python": {".py"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "go": {".go"},
    "rust": {".rs"},
    "java": {".java"},
    "cpp": {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx"},
    "csharp": {".cs"},
    "ruby": {".rb"},
    "php": {".php"},
    "swift": {".swift"},
    "kotlin": {".kt", ".kts"},
    "scala": {".scala"},
}

# 默认忽略的目录名
DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git", ".svn", ".hg",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", ".venv", "venv", "env",
    ".tox", ".nox",
    "build", "dist", ".eggs",
    ".idea", ".vscode",
    ".codegraph_cache",
    "vendor",  # Go vendor
    "target",  # Rust/Java target
}


class FileWalker:
    """项目文件遍历器

    递归遍历项目目录，收集指定语言的代码文件。
    支持按语言过滤和忽略特定目录。
    """

    def __init__(
        self,
        root_path: str,
        language: Optional[str] = None,
        extensions: Optional[Set[str]] = None,
        ignore_dirs: Optional[Set[str]] = None,
    ):
        """初始化文件遍历器

        Args:
            root_path: 项目根目录路径
            language: 指定语言（可选），优先级高于 extensions
            extensions: 自定义文件扩展名集合
            ignore_dirs: 自定义忽略目录集合
        """
        self.root_path = os.path.abspath(root_path)
        self.language = language
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.ignore_dirs = ignore_dirs or DEFAULT_IGNORE_DIRS

        # 如果指定了语言，使用对应的扩展名
        if language:
            lang_lower = language.lower()
            if lang_lower in LANGUAGE_EXTENSIONS:
                self.extensions = LANGUAGE_EXTENSIONS[lang_lower]
            elif lang_lower == "javascript":
                # JavaScript 包含 TypeScript
                self.extensions = (
                    LANGUAGE_EXTENSIONS["javascript"]
                    | LANGUAGE_EXTENSIONS["typescript"]
                )

    def walk(self) -> List[str]:
        """遍历项目目录，收集代码文件

        Returns:
            代码文件路径列表（绝对路径）
        """
        files: List[str] = []

        if not os.path.isdir(self.root_path):
            return files

        for dirpath, dirnames, filenames in os.walk(self.root_path):
            # 过滤忽略的目录（原地修改 dirnames 以阻止 os.walk 递归进入）
            dirnames[:] = [
                d for d in dirnames
                if d not in self.ignore_dirs
                and not d.startswith(".")
                and not d.startswith("__")
            ]

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.extensions:
                    full_path = os.path.join(dirpath, filename)
                    files.append(full_path)

        return sorted(files)

    def count_by_extension(self) -> dict:
        """统计各扩展名的文件数量

        Returns:
            扩展名 -> 文件数量 的映射
        """
        files = self.walk()
        counts: dict = {}
        for fp in files:
            ext = os.path.splitext(fp)[1].lower()
            counts[ext] = counts.get(ext, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
