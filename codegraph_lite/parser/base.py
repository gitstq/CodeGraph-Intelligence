"""
解析器基类

定义所有代码解析器的通用接口和数据结构。
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CodeElement:
    """代码元素基类"""
    name: str
    element_type: str  # function, class, variable, import, module
    line_start: int
    line_end: int = 0
    file_path: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class FunctionDef(CodeElement):
    """函数定义"""
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    complexity: int = 0
    calls: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.element_type = "function"


@dataclass
class ClassDef(CodeElement):
    """类定义"""
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.element_type = "class"


@dataclass
class ImportDef(CodeElement):
    """导入定义"""
    module: str = ""
    alias: str = ""
    names: List[str] = field(default_factory=list)
    is_from_import: bool = False

    def __post_init__(self):
        self.element_type = "import"


@dataclass
class VariableDef(CodeElement):
    """变量定义"""
    var_type: str = ""
    value: str = ""

    def __post_init__(self):
        self.element_type = "variable"


@dataclass
class ParseResult:
    """解析结果"""
    file_path: str = ""
    language: str = ""
    functions: List[FunctionDef] = field(default_factory=list)
    classes: List[ClassDef] = field(default_factory=list)
    imports: List[ImportDef] = field(default_factory=list)
    variables: List[VariableDef] = field(default_factory=list)
    calls: List[Tuple[str, str, int]] = field(default_factory=list)  # (caller, callee, line)
    loc: int = 0
    lines: List[str] = field(default_factory=list)

    def all_elements(self) -> List[CodeElement]:
        """获取所有代码元素"""
        elements: List[CodeElement] = []
        elements.extend(self.functions)
        elements.extend(self.classes)
        elements.extend(self.imports)
        elements.extend(self.variables)
        return elements

    def summary(self) -> Dict:
        """获取解析摘要"""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "loc": self.loc,
            "function_count": len(self.functions),
            "class_count": len(self.classes),
            "import_count": len(self.imports),
            "variable_count": len(self.variables),
            "call_count": len(self.calls),
        }


class BaseParser:
    """代码解析器基类

    所有语言解析器都应继承此类并实现相应的解析方法。
    使用正则表达式提取代码结构信息。
    """

    # 语言名称
    language: str = "unknown"

    # 文件扩展名
    extensions: List[str] = []

    # 注释模式（用于去除注释）
    comment_patterns: List[re.Pattern] = []

    # 字符串模式（用于去除字符串内容）
    string_pattern: Optional[re.Pattern] = None

    def parse(self, source: str, file_path: str = "") -> ParseResult:
        """解析源代码

        Args:
            source: 源代码文本
            file_path: 文件路径（用于错误报告和定位）

        Returns:
            ParseResult 解析结果
        """
        result = ParseResult(
            file_path=file_path,
            language=self.language,
            lines=source.splitlines(),
            loc=self._count_loc(source),
        )

        # 清理源代码（去除注释和字符串）
        cleaned = self._clean_source(source)

        # 提取各类代码元素
        result.functions = self.parse_functions(cleaned, source)
        result.classes = self.parse_classes(cleaned, source)
        result.imports = self.parse_imports(cleaned)
        result.variables = self.parse_variables(cleaned)
        result.calls = self.parse_calls(cleaned)

        # 设置文件路径
        for elem in result.all_elements():
            elem.file_path = file_path

        return result

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析函数定义

        Args:
            cleaned_source: 清理后的源代码
            raw_source: 原始源代码（用于提取文档字符串等）

        Returns:
            函数定义列表
        """
        return []

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """解析类定义

        Args:
            cleaned_source: 清理后的源代码
            raw_source: 原始源代码

        Returns:
            类定义列表
        """
        return []

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析导入语句

        Args:
            cleaned_source: 清理后的源代码

        Returns:
            导入定义列表
        """
        return []

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """解析变量定义

        Args:
            cleaned_source: 清理后的源代码

        Returns:
            变量定义列表
        """
        return []

    def parse_calls(
        self, cleaned_source: str
    ) -> List[Tuple[str, str, int]]:
        """解析函数调用关系

        Args:
            cleaned_source: 清理后的源代码

        Returns:
            调用关系列表 (caller, callee, line_number)
        """
        return []

    def _clean_source(self, source: str) -> str:
        """清理源代码，去除注释和字符串内容

        Args:
            source: 原始源代码

        Returns:
            清理后的源代码
        """
        cleaned = source

        # 去除多行注释
        for pattern in self.comment_patterns:
            cleaned = pattern.sub("", cleaned)

        # 去除字符串（保留位置以维持行号）
        if self.string_pattern:
            cleaned = self.string_pattern.sub('""', cleaned)

        return cleaned

    def _count_loc(self, source: str) -> int:
        """计算有效代码行数（去除空行和纯注释行）

        Args:
            source: 源代码

        Returns:
            有效代码行数
        """
        count = 0
        for line in source.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1
        return count

    def _find_line_number(self, source: str, position: int) -> int:
        """根据字符位置查找行号

        Args:
            source: 源代码
            position: 字符位置

        Returns:
            行号（从1开始）
        """
        return source[:position].count("\n") + 1

    def _extract_docstring_python(self, source: str, start_pos: int) -> str:
        """从Python源代码中提取文档字符串

        Args:
            source: 原始源代码
            start_pos: 定义开始位置

        Returns:
            文档字符串
        """
        # 查找函数/类定义后的第一个三引号字符串
        triple_quote = re.search(r'"""(.*?)"""', source[start_pos:start_pos + 500], re.DOTALL)
        if triple_quote:
            return triple_quote.group(1).strip()
        triple_quote = re.search(r"'''(.*?)'''", source[start_pos:start_pos + 500], re.DOTALL)
        if triple_quote:
            return triple_quote.group(1).strip()
        return ""
