"""
Python 代码解析器

使用正则表达式解析 Python 源代码，提取函数、类、导入、变量和调用关系。
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


class PythonParser(BaseParser):
    """Python 代码解析器"""

    language = "python"
    extensions = [".py"]

    def __init__(self):
        super().__init__()
        # Python 注释模式
        self.comment_patterns = [
            # 多行注释（三引号字符串作为注释的情况）
            re.compile(r'""".*?"""', re.DOTALL),
            re.compile(r"'''.*?'''", re.DOTALL),
            # 单行注释
            re.compile(r"#.*$"),
        ]
        # Python 字符串模式
        self.string_pattern = re.compile(
            r'(f?"""[\s\S]*?"""|f?\'\'\'[\s\S]*?\'\'\'|f?"[^"]*"|f?\'[^\']*\')',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析 Python 函数定义

        匹配模式：
        - def function_name(params):
        - async def function_name(params):
        - @decorator (在函数定义上方)
        """
        functions: List[FunctionDef] = []

        # 匹配函数定义（包括 async def）
        pattern = re.compile(
            r"^(async\s+)?def\s+(\w+)\s*\(([^)]*)\)"
            r"(?:\s*->\s*([^\n:]+))?\s*:",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            is_async = bool(match.group(1))
            name = match.group(2)
            params_str = match.group(3).strip()
            return_type = (match.group(4) or "").strip()
            line_start = cleaned_source[:match.start()].count("\n") + 1

            # 提取参数列表
            parameters = self._parse_parameters(params_str)

            # 提取文档字符串
            docstring = self._extract_docstring_python(
                raw_source, match.start()
            )

            # 提取装饰器
            decorators = self._extract_decorators(cleaned_source, match.start())

            # 计算函数体范围
            line_end = self._find_function_end(cleaned_source, match.end())

            # 计算圈复杂度
            func_body = self._extract_function_body(cleaned_source, match.end())
            complexity = self._calc_complexity(func_body)

            # 提取函数调用
            calls = self._extract_function_calls(func_body)

            func = FunctionDef(
                name=f"{'async ' if is_async else ''}{name}",
                element_type="function",
                line_start=line_start,
                line_end=line_end,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                decorators=decorators,
                complexity=complexity,
                calls=calls,
                metadata={"is_async": is_async},
            )
            functions.append(func)

        return functions

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """解析 Python 类定义

        匹配模式：
        - class ClassName:
        - class ClassName(BaseClass):
        - class ClassName(Base1, Base2):
        """
        classes: List[ClassDef] = []

        pattern = re.compile(
            r"^class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            bases_str = (match.group(2) or "").strip()
            line_start = cleaned_source[:match.start()].count("\n") + 1

            # 提取基类
            bases = [b.strip() for b in bases_str.split(",") if b.strip()] if bases_str else []

            # 提取文档字符串
            docstring = self._extract_docstring_python(
                raw_source, match.start()
            )

            # 提取装饰器
            decorators = self._extract_decorators(cleaned_source, match.start())

            # 提取类中的方法
            class_body = self._extract_class_body(cleaned_source, match.end())
            methods = re.findall(r"def\s+(\w+)\s*\(", class_body)

            # 类体范围
            line_end = self._find_class_end(cleaned_source, match.end())

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                bases=bases,
                methods=methods,
                docstring=docstring,
                decorators=decorators,
            )
            classes.append(cls)

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析 Python 导入语句

        匹配模式：
        - import module
        - import module as alias
        - from module import name
        - from module import name as alias
        - from module import (name1, name2)
        """
        imports: List[ImportDef] = []

        # from ... import ...
        from_pattern = re.compile(
            r"^from\s+([\w.]+)\s+import\s+(.+)$",
            re.MULTILINE,
        )
        for match in from_pattern.finditer(cleaned_source):
            module = match.group(1)
            names_str = match.group(2).strip().rstrip(",")
            line_num = cleaned_source[:match.start()].count("\n") + 1

            # 处理多行导入和括号
            names_str = re.sub(r"\s*\(\s*", "", names_str)
            names_str = re.sub(r"\s*\)\s*", "", names_str)
            names_str = re.sub(r"\s+", " ", names_str)

            names = []
            aliases = {}
            for part in names_str.split(","):
                part = part.strip()
                if not part:
                    continue
                if " as " in part:
                    orig, alias = part.split(" as ", 1)
                    names.append(orig.strip())
                    aliases[orig.strip()] = alias.strip()
                else:
                    names.append(part)

            imp = ImportDef(
                name=f"from {module} import ...",
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                names=names,
                is_from_import=True,
                metadata={"aliases": aliases},
            )
            imports.append(imp)

        # import ...
        import_pattern = re.compile(
            r"^import\s+([\w.]+)(?:\s+as\s+(\w+))?",
            re.MULTILINE,
        )
        for match in import_pattern.finditer(cleaned_source):
            module = match.group(1)
            alias = match.group(2) or ""
            line_num = cleaned_source[:match.start()].count("\n") + 1

            imp = ImportDef(
                name=module,
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
        """解析 Python 模块级变量定义

        匹配模式：
        - VAR_NAME = value
        - VAR_NAME: type = value
        """
        variables: List[VariableDef] = []

        # 简单的模块级变量（不匹配函数/类内部的）
        pattern = re.compile(
            r"^([A-Z_][A-Z0-9_]*)\s*(?::\s*([^\n=]+))?\s*=\s*(.+)$",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            var_type = (match.group(2) or "").strip()
            value = match.group(3).strip()[:50]  # 截断过长的值
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
        """解析函数调用关系

        匹配模式：
        - function_name(args)
        - module.function_name(args)
        - obj.method_name(args)
        """
        calls: List[Tuple[str, str, int]] = []

        # 首先找到所有函数定义的位置，用于确定 caller
        func_pattern = re.compile(
            r"^(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE
        )
        func_ranges: List[Tuple[str, int, int]] = []
        for match in func_pattern.finditer(cleaned_source):
            func_name = match.group(1)
            start = match.start()
            end = self._find_function_end_pos(cleaned_source, match.end())
            func_ranges.append((func_name, start, end))

        # 查找所有函数调用
        call_pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")

        for caller, start, end in func_ranges:
            body = cleaned_source[start:end]
            seen = set()
            for call_match in call_pattern.finditer(body):
                callee = call_match.group(1)
                # 去除内置函数和关键字
                if callee in _PYTHON_BUILTINS:
                    continue
                if callee in seen:
                    continue
                seen.add(callee)
                line_num = cleaned_source[:start + call_match.start()].count("\n") + 1
                calls.append((caller, callee, line_num))

        return calls

    # ── 私有辅助方法 ──

    def _parse_parameters(self, params_str: str) -> List[str]:
        """解析函数参数列表"""
        if not params_str:
            return []
        params = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue
            # 去除类型注解和默认值
            name = param.split(":")[0].split("=")[0].strip()
            # 去除 * 和 ** 前缀但保留标记
            if name.startswith("**"):
                name = "**" + name[2:].strip()
            elif name.startswith("*"):
                name = "*" + name[1:].strip()
            if name and name != "self" and name != "cls":
                params.append(name)
        return params

    def _extract_decorators(
        self, source: str, def_start: int
    ) -> List[str]:
        """提取函数/类定义上方的装饰器"""
        decorators: List[str] = []
        # 向上查找 @decorator 行
        pos = def_start
        while pos > 0:
            # 找到上一行
            newline_pos = source.rfind("\n", 0, pos)
            if newline_pos == -1:
                break
            line_start = newline_pos + 1
            line = source[line_start:pos].strip()
            if line.startswith("@"):
                # 提取装饰器名称
                dec = line[1:].split("(")[0].strip()
                decorators.insert(0, dec)
                pos = line_start
            else:
                break
        return decorators

    def _find_function_end(self, source: str, body_start: int) -> int:
        """查找函数体的结束行号"""
        end_pos = self._find_function_end_pos(source, body_start)
        return source[:end_pos].count("\n") + 1

    def _find_function_end_pos(self, source: str, body_start: int) -> int:
        """查找函数体的结束位置（字符偏移）"""
        lines = source[body_start:].splitlines()
        if not lines:
            return body_start

        base_indent = len(lines[0]) - len(lines[0].lstrip())
        if base_indent == 0 and lines[0].strip():
            # 单行函数
            return body_start + len(lines[0]) + 1

        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                return body_start + sum(len(l) + 1 for l in lines[:i])

        return len(source)

    def _find_class_end(self, source: str, body_start: int) -> int:
        """查找类体的结束行号"""
        end_pos = self._find_function_end_pos(source, body_start)
        return source[:end_pos].count("\n") + 1

    def _extract_function_body(self, source: str, body_start: int) -> str:
        """提取函数体代码"""
        end_pos = self._find_function_end_pos(source, body_start)
        return source[body_start:end_pos]

    def _extract_class_body(self, source: str, body_start: int) -> str:
        """提取类体代码"""
        end_pos = self._find_function_end_pos(source, body_start)
        return source[body_start:end_pos]

    def _extract_function_calls(self, body: str) -> List[str]:
        """从函数体中提取被调用的函数名"""
        calls = []
        pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")
        seen = set()
        for match in pattern.finditer(body):
            name = match.group(1)
            if name not in _PYTHON_BUILTINS and name not in seen:
                calls.append(name)
                seen.add(name)
        return calls

    def _calc_complexity(self, body: str) -> int:
        """计算圈复杂度

        基于分支关键字计数：
        if, elif, for, while, except, and, or, with (Python特有)
        每个分支关键字增加1，基础复杂度为1
        """
        complexity = 1

        # 分支关键字
        branch_patterns = [
            (r"\bif\b", 1),
            (r"\belif\b", 1),
            (r"\bfor\b", 1),
            (r"\bwhile\b", 1),
            (r"\bexcept\b", 1),
            (r"\band\b", 1),
            (r"\bor\b", 1),
            (r"\bwith\b", 1),
        ]

        for pattern_str, weight in branch_patterns:
            matches = re.findall(pattern_str, body)
            complexity += len(matches) * weight

        # 三元表达式 a if cond else b
        ternary = re.findall(r"\bif\b.+?\belse\b", body)
        complexity += len(ternary)

        return complexity


# Python 内置函数集合（用于过滤调用关系）
_PYTHON_BUILTINS = {
    "print", "len", "range", "str", "int", "float", "list", "dict", "set",
    "tuple", "bool", "bytes", "bytearray", "type", "isinstance", "issubclass",
    "hasattr", "getattr", "setattr", "delattr", "callable", "super", "property",
    "staticmethod", "classmethod", "enumerate", "zip", "map", "filter", "sorted",
    "reversed", "iter", "next", "open", "input", "abs", "max", "min", "sum",
    "round", "pow", "divmod", "all", "any", "chr", "ord", "hex", "oct", "bin",
    "id", "hash", "repr", "format", "vars", "dir", "help", "eval", "exec",
    "compile", "__import__", "breakpoint", "memoryview", "complex", "frozenset",
    "slice", "object", "Exception", "ValueError", "TypeError", "KeyError",
    "IndexError", "AttributeError", "RuntimeError", "StopIteration",
    "NotImplementedError", "IOError", "OSError", "FileNotFoundError",
    "ImportError", "ModuleNotFoundError", "AssertionError", "True", "False",
    "None",
}
