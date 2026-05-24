"""
代码解析器模块

提供多语言代码解析器，使用正则表达式提取代码结构信息。
支持 Python、JavaScript/TypeScript、Go、Rust、Java 和通用文本解析。
"""

from .base import BaseParser, ParseResult
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser
from .go_parser import GoParser
from .rust_parser import RustParser
from .java_parser import JavaParser
from .generic_parser import GenericParser

# 语言 -> 解析器映射
PARSER_REGISTRY = {
    ".py": PythonParser,
    ".js": JavaScriptParser,
    ".jsx": JavaScriptParser,
    ".ts": JavaScriptParser,
    ".tsx": JavaScriptParser,
    ".mjs": JavaScriptParser,
    ".cjs": JavaScriptParser,
    ".go": GoParser,
    ".rs": RustParser,
    ".java": JavaParser,
}


def get_parser(file_path: str, language: str = None) -> BaseParser:
    """根据文件扩展名获取对应的解析器

    Args:
        file_path: 文件路径
        language: 指定语言（可选），优先级高于文件扩展名

    Returns:
        对应的解析器实例
    """
    import os

    if language:
        lang_map = {
            "python": PythonParser,
            "javascript": JavaScriptParser,
            "typescript": JavaScriptParser,
            "go": GoParser,
            "rust": RustParser,
            "java": JavaParser,
        }
        parser_cls = lang_map.get(language.lower())
        if parser_cls:
            return parser_cls()

    ext = os.path.splitext(file_path)[1].lower()
    parser_cls = PARSER_REGISTRY.get(ext, GenericParser)
    return parser_cls()


__all__ = [
    "BaseParser",
    "ParseResult",
    "PythonParser",
    "JavaScriptParser",
    "GoParser",
    "RustParser",
    "JavaParser",
    "GenericParser",
    "get_parser",
    "PARSER_REGISTRY",
]
