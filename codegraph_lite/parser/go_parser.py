"""
Go 代码解析器

使用正则表达式解析 Go 源代码，提取函数、结构体、接口、导入和调用关系。
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


class GoParser(BaseParser):
    """Go 代码解析器"""

    language = "go"
    extensions = [".go"]

    def __init__(self):
        super().__init__()
        # Go 注释模式
        self.comment_patterns = [
            re.compile(r"/\*[\s\S]*?\*/"),  # 多行注释
            re.compile(r"//.*$"),  # 单行注释
        ]
        # Go 字符串模式
        self.string_pattern = re.compile(
            r'`[^`]*`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析 Go 函数定义

        匹配模式：
        - func Name(params) returnType { }
        - func (receiver) Name(params) returnType { }
        - func Name(params) (returnTypes) { }
        """
        functions: List[FunctionDef] = []

        # 匹配函数定义
        pattern = re.compile(
            r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)"
            r"(?:\s*\(([^)]*)\)|\s+([^{]+))?\s*\{",
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            params_str = match.group(2).strip()
            # 返回类型可能在括号内或直接写
            return_type = ""
            if match.group(3):
                return_type = match.group(3).strip()
            elif match.group(4):
                return_type = match.group(4).strip()

            line_start = cleaned_source[:match.start()].count("\n") + 1

            parameters = self._parse_parameters(params_str)
            line_end = self._find_block_end(cleaned_source, match.end() - 1)
            func_body = self._extract_block_body(cleaned_source, match.end() - 1)
            complexity = self._calc_complexity(func_body)
            calls = self._extract_function_calls(func_body)

            func = FunctionDef(
                name=name,
                element_type="function",
                line_start=line_start,
                line_end=line_end,
                parameters=parameters,
                return_type=return_type,
                complexity=complexity,
                calls=calls,
            )
            functions.append(func)

        return functions

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """解析 Go 结构体和接口定义

        匹配模式：
        - type Name struct { }
        - type Name interface { }
        """
        classes: List[ClassDef] = []

        # 结构体
        struct_pattern = re.compile(
            r"type\s+(\w+)\s+struct\s*\{",
        )
        for match in struct_pattern.finditer(cleaned_source):
            name = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            struct_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(r"(\w+)\s*\(", struct_body)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                methods=methods,
                metadata={"kind": "struct"},
            )
            classes.append(cls)

        # 接口
        interface_pattern = re.compile(
            r"type\s+(\w+)\s+interface\s*\{",
        )
        for match in interface_pattern.finditer(cleaned_source):
            name = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            iface_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(r"(\w+)\s*\(", iface_body)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                methods=methods,
                metadata={"kind": "interface"},
            )
            classes.append(cls)

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析 Go 导入语句

        匹配模式：
        - import "package"
        - import alias "package"
        - import ( "pkg1" "pkg2" )
        """
        imports: List[ImportDef] = []

        # 单行导入
        single_pattern = re.compile(
            r'import\s+(?:([A-Za-z_]\w*)\s+)?"([^"]+)"',
        )
        for match in single_pattern.finditer(cleaned_source):
            alias = match.group(1) or ""
            module = match.group(2)
            line_num = cleaned_source[:match.start()].count("\n") + 1

            imp = ImportDef(
                name=alias or module.split("/")[-1],
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                alias=alias,
                is_from_import=False,
            )
            imports.append(imp)

        # 多行导入
        multi_pattern = re.compile(
            r"import\s*\(\s*(.*?)\s*\)",
            re.DOTALL,
        )
        for match in multi_pattern.finditer(cleaned_source):
            block = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1

            # 提取每个导入
            imp_pattern = re.compile(r'(?:([A-Za-z_]\w*)\s+)?"([^"]+)"')
            for imp_match in imp_pattern.finditer(block):
                alias = imp_match.group(1) or ""
                module = imp_match.group(2)
                line_num = line_start + block[:imp_match.start()].count("\n")

                imp = ImportDef(
                    name=alias or module.split("/")[-1],
                    element_type="import",
                    line_start=line_num,
                    line_end=line_num,
                    module=module,
                    alias=alias,
                    is_from_import=False,
                )
                imports.append(imp)

        return imports

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """解析 Go 变量定义

        匹配模式：
        - var Name type = value
        - var Name = value
        - const Name = value
        - Name := value
        """
        variables: List[VariableDef] = []

        # var 声明
        var_pattern = re.compile(
            r"var\s+([A-Z_][A-Z0-9_]*)\s*(?:\([^)]+\)|([^\n=]+))?(?:=\s*(.+))?",
            re.MULTILINE,
        )
        for match in var_pattern.finditer(cleaned_source):
            name = match.group(1)
            var_type = (match.group(2) or "").strip()
            value = (match.group(3) or "").strip()[:50]
            line_num = cleaned_source[:match.start()].count("\n") + 1

            var = VariableDef(
                name=name,
                element_type="variable",
                line_start=line_num,
                line_end=line_num,
                var_type=var_type,
                value=value,
            )
            variables.append(var)

        # const 声明
        const_pattern = re.compile(
            r"const\s+([A-Z_][A-Z0-9_]*)\s*(?:([^\n=]+))?(?:=\s*(.+))?",
            re.MULTILINE,
        )
        for match in const_pattern.finditer(cleaned_source):
            name = match.group(1)
            var_type = (match.group(2) or "").strip()
            value = (match.group(3) or "").strip()[:50]
            line_num = cleaned_source[:match.start()].count("\n") + 1

            var = VariableDef(
                name=name,
                element_type="variable",
                line_start=line_num,
                line_end=line_num,
                var_type=var_type,
                value=value,
            )
            variables.append(var)

        return variables

    def parse_calls(
        self, cleaned_source: str
    ) -> List[Tuple[str, str, int]]:
        """解析函数调用关系"""
        calls: List[Tuple[str, str, int]] = []

        # 找到所有函数定义
        func_pattern = re.compile(r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(")
        func_ranges: List[Tuple[str, int, int]] = []
        for match in func_pattern.finditer(cleaned_source):
            func_name = match.group(1)
            start = match.start()
            end = self._find_block_end_pos(cleaned_source, match.end() - 1)
            func_ranges.append((func_name, start, end))

        call_pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")

        for caller, start, end in func_ranges:
            body = cleaned_source[start:end]
            seen = set()
            for call_match in call_pattern.finditer(body):
                callee = call_match.group(1)
                if callee in _GO_BUILTINS or callee in seen:
                    continue
                seen.add(callee)
                line_num = cleaned_source[:start + call_match.start()].count("\n") + 1
                calls.append((caller, callee, line_num))

        return calls

    # ── 私有辅助方法 ──

    def _parse_parameters(self, params_str: str) -> List[str]:
        """解析 Go 函数参数"""
        if not params_str:
            return []
        params = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue
            # Go 参数格式: name type 或仅 type
            parts = param.split()
            if len(parts) >= 2:
                params.append(parts[0])
            elif len(parts) == 1:
                params.append(parts[0])
        return params

    def _find_block_end(self, source: str, open_brace: int) -> int:
        """查找花括号块的结束行号"""
        end_pos = self._find_block_end_pos(source, open_brace)
        return source[:end_pos].count("\n") + 1

    def _find_block_end_pos(self, source: str, open_brace: int) -> int:
        """查找花括号块的结束位置"""
        depth = 0
        i = open_brace
        while i < len(source):
            ch = source[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return len(source)

    def _extract_block_body(self, source: str, open_brace: int) -> str:
        """提取花括号块内容"""
        end_pos = self._find_block_end_pos(source, open_brace)
        return source[open_brace + 1:end_pos - 1]

    def _extract_function_calls(self, body: str) -> List[str]:
        """从函数体中提取被调用的函数名"""
        calls = []
        pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")
        seen = set()
        for match in pattern.finditer(body):
            name = match.group(1)
            if name not in _GO_BUILTINS and name not in seen:
                calls.append(name)
                seen.add(name)
        return calls

    def _calc_complexity(self, body: str) -> int:
        """计算圈复杂度"""
        complexity = 1
        branch_patterns = [
            (r"\bif\b", 1),
            (r"\belse\s+if\b", 1),
            (r"\bfor\b", 1),
            (r"\bcase\b", 1),
            (r"\bselect\b", 1),
            (r"\bgo\b", 1),
            (r"\bdefer\b", 0),
            (r"\&\&", 1),
            (r"\|\|", 1),
        ]
        for pattern_str, weight in branch_patterns:
            matches = re.findall(pattern_str, body)
            complexity += len(matches) * weight
        return complexity


_GO_BUILTINS = {
    "fmt", "println", "printf", "scanf", "make", "new", "len", "cap",
    "append", "copy", "delete", "close", "panic", "recover", "print",
    "true", "false", "nil", "iota", "string", "int", "int8", "int16",
    "int32", "int64", "uint", "uint8", "uint16", "uint32", "uint64",
    "float32", "float64", "complex64", "complex128", "byte", "rune",
    "error", "bool", "true", "false", "nil",
}
