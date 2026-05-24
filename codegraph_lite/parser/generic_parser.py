"""
通用文本解析器

作为后备解析器，对不支持的文件类型进行基本的文本分析。
提取简单的函数定义模式和导入语句。
"""

import re
from typing import List, Tuple

from .base import (
    BaseParser,
    ClassDef,
    FunctionDef,
    ImportDef,
    ParseResult,
    VariableDef,
)


class GenericParser(BaseParser):
    """通用文本解析器

    对不支持的文件类型进行基本的文本分析。
    使用宽松的正则表达式匹配常见的代码模式。
    """

    language = "generic"
    extensions: List[str] = []

    def __init__(self):
        super().__init__()
        # 通用注释模式
        self.comment_patterns = [
            re.compile(r"/\*[\s\S]*?\*/"),  # C风格多行注释
            re.compile(r"//.*$"),  # C风格单行注释
            re.compile(r"#.*$"),  # Shell/Python风格注释
            re.compile(r"--.*$"),  # SQL/Lua风格注释
        ]
        # 通用字符串模式
        self.string_pattern = re.compile(
            r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`[^`]*`',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """尝试从通用文本中提取函数定义

        匹配多种常见模式：
        - function name(params)
        - def name(params):
        - func name(params)
        - fn name(params)
        - name(params) {
        """
        functions: List[FunctionDef] = []

        patterns = [
            # function name(params)
            re.compile(
                r"function\s+(\w+)\s*\(([^)]*)\)\s*\{?",
                re.MULTILINE,
            ),
            # def name(params):
            re.compile(
                r"def\s+(\w+)\s*\(([^)]*)\)\s*:?",
                re.MULTILINE,
            ),
            # func name(params)
            re.compile(
                r"func\s+(\w+)\s*\(([^)]*)\)\s*\{?",
                re.MULTILINE,
            ),
            # fn name(params)
            re.compile(
                r"fn\s+(\w+)\s*\(([^)]*)\)\s*\{?",
                re.MULTILINE,
            ),
        ]

        seen = set()
        for pattern in patterns:
            for match in pattern.finditer(cleaned_source):
                name = match.group(1)
                if name in seen:
                    continue
                seen.add(name)

                params_str = match.group(2).strip()
                line_start = cleaned_source[:match.start()].count("\n") + 1
                parameters = [p.strip() for p in params_str.split(",") if p.strip()]

                func = FunctionDef(
                    name=name,
                    element_type="function",
                    line_start=line_start,
                    line_end=line_start,
                    parameters=parameters,
                    complexity=1,
                )
                functions.append(func)

        return functions

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """尝试从通用文本中提取类定义"""
        classes: List[ClassDef] = []

        patterns = [
            # class Name
            re.compile(
                r"class\s+(\w+)(?:\s*:\s*([^{]+))?\s*\{?",
                re.MULTILINE,
            ),
            # struct Name
            re.compile(
                r"struct\s+(\w+)\s*\{?",
                re.MULTILINE,
            ),
            # interface Name
            re.compile(
                r"interface\s+(\w+)\s*\{?",
                re.MULTILINE,
            ),
        ]

        seen = set()
        for pattern in patterns:
            for match in pattern.finditer(cleaned_source):
                name = match.group(1)
                if name in seen:
                    continue
                seen.add(name)

                bases_str = match.group(2) or ""
                bases = [b.strip() for b in bases_str.split(",") if b.strip()]

                line_start = cleaned_source[:match.start()].count("\n") + 1

                cls = ClassDef(
                    name=name,
                    element_type="class",
                    line_start=line_start,
                    line_end=line_start,
                    bases=bases,
                )
                classes.append(cls)

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """尝试从通用文本中提取导入语句"""
        imports: List[ImportDef] = []

        patterns = [
            # import "module"
            re.compile(r'import\s+["\']([^"\']+)["\']'),
            # import module
            re.compile(r"import\s+([\w.]+)"),
            # require("module")
            re.compile(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            # include "file"
            re.compile(r'include\s*[<"]([^>"]+)[>"]'),
            # from module import
            re.compile(r"from\s+([\w.]+)\s+import"),
            # use module
            re.compile(r"use\s+([\w:]+)"),
        ]

        seen = set()
        for pattern in patterns:
            for match in pattern.finditer(cleaned_source):
                module = match.group(1)
                if module in seen:
                    continue
                seen.add(module)

                line_num = cleaned_source[:match.start()].count("\n") + 1

                imp = ImportDef(
                    name=module,
                    element_type="import",
                    line_start=line_num,
                    line_end=line_num,
                    module=module,
                    is_from_import=False,
                )
                imports.append(imp)

        return imports

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """尝试从通用文本中提取常量定义"""
        variables: List[VariableDef] = []

        pattern = re.compile(
            r"(?:const|let|var|final)\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;\n]+)",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            value = match.group(2).strip()[:50]
            line_num = cleaned_source[:match.start()].count("\n") + 1

            var = VariableDef(
                name=name,
                element_type="variable",
                line_start=line_num,
                line_end=line_num,
                value=value,
            )
            variables.append(var)

        return variables

    def parse_calls(
        self, cleaned_source: str
    ) -> List[Tuple[str, str, int]]:
        """通用调用关系解析（简单实现）"""
        return []
