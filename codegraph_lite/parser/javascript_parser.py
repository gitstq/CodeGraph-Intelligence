"""
JavaScript/TypeScript 代码解析器

使用正则表达式解析 JavaScript 和 TypeScript 源代码，
提取函数、类、导入、变量和调用关系。
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


class JavaScriptParser(BaseParser):
    """JavaScript/TypeScript 代码解析器"""

    language = "javascript"
    extensions = [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def __init__(self):
        super().__init__()
        # JS/TS 注释模式
        self.comment_patterns = [
            re.compile(r"/\*[\s\S]*?\*/"),  # 多行注释 /* */
            re.compile(r"//.*$"),  # 单行注释 //
        ]
        # JS/TS 字符串模式
        self.string_pattern = re.compile(
            r'(`[^`]*`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析 JavaScript/TypeScript 函数定义

        匹配模式：
        - function name(params) { }
        - async function name(params) { }
        - const name = (params) => { }
        - const name = function(params) { }
        - export function name(params) { }
        - export default function name(params) { }
        - name(params) { }  (方法定义)
        """
        functions: List[FunctionDef] = []

        # 模式1: function 声明
        func_pattern = re.compile(
            r"(?:export\s+(?:default\s+)?)?"
            r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"
            r"(?:\s*:\s*([^{]+))?\s*\{",
        )

        for match in func_pattern.finditer(cleaned_source):
            name = match.group(1)
            params_str = match.group(2).strip()
            return_type = (match.group(3) or "").strip()
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
                metadata={"kind": "function_declaration"},
            )
            functions.append(func)

        # 模式2: 箭头函数 const name = (params) => { }
        arrow_pattern = re.compile(
            r"(?:export\s+(?:default\s+)?)?"
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?"
            r"\(([^)]*)\)(?:\s*:\s*([^{=]+))?\s*=>",
        )

        for match in arrow_pattern.finditer(cleaned_source):
            name = match.group(1)
            params_str = match.group(2).strip()
            return_type = (match.group(3) or "").strip()
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
                metadata={"kind": "arrow_function"},
            )
            functions.append(func)

        # 模式3: 单参数箭头函数 const name = param => { }
        arrow_single = re.compile(
            r"(?:export\s+(?:default\s+)?)?"
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?"
            r"(\w+)\s*=>",
        )

        for match in arrow_single.finditer(cleaned_source):
            name = match.group(1)
            param = match.group(2)
            line_start = cleaned_source[:match.start()].count("\n") + 1

            line_end = self._find_block_end(cleaned_source, match.end() - 1)
            func_body = self._extract_block_body(cleaned_source, match.end() - 1)
            complexity = self._calc_complexity(func_body)
            calls = self._extract_function_calls(func_body)

            func = FunctionDef(
                name=name,
                element_type="function",
                line_start=line_start,
                line_end=line_end,
                parameters=[param],
                complexity=complexity,
                calls=calls,
                metadata={"kind": "arrow_function_single"},
            )
            functions.append(func)

        return functions

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """解析 JavaScript/TypeScript 类定义

        匹配模式：
        - class Name { }
        - class Name extends Base { }
        - export class Name { }
        - export default class Name { }
        """
        classes: List[ClassDef] = []

        pattern = re.compile(
            r"(?:export\s+(?:default\s+)?)?"
            r"class\s+(\w+)(?:\s+extends\s+([\w.]+))?\s*\{",
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            base = match.group(2) or ""
            line_start = cleaned_source[:match.start()].count("\n") + 1

            bases = [base] if base else []

            class_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(
                r"(?:async\s+)?(\w+)\s*\([^)]*\)(?:\s*:\s*[^{]+)?\s*\{",
                class_body,
            )

            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                bases=bases,
                methods=methods,
            )
            classes.append(cls)

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析 JavaScript/TypeScript 导入语句

        匹配模式：
        - import Name from 'module'
        - import { Name1, Name2 } from 'module'
        - import * as Name from 'module'
        - import 'module'
        - require('module')
        """
        imports: List[ImportDef] = []

        # ES6 import
        import_pattern = re.compile(
            r"import\s+"
            r"(?:(\w+)\s*,?\s*|"
            r"\*\s+as\s+(\w+)\s*,?\s*|"
            r"\{([^}]*)\}\s*,?\s*)?"
            r"from\s+['\"]([^'\"]+)['\"]",
        )

        for match in import_pattern.finditer(cleaned_source):
            default_name = match.group(1) or ""
            namespace_alias = match.group(2) or ""
            named_imports = match.group(3) or ""
            module = match.group(4)
            line_num = cleaned_source[:match.start()].count("\n") + 1

            names = []
            if default_name:
                names.append(default_name)
            if namespace_alias:
                names.append(f"* as {namespace_alias}")
            if named_imports:
                for name in named_imports.split(","):
                    name = name.strip()
                    if name:
                        # 处理 as 别名
                        if " as " in name:
                            names.append(name)
                        else:
                            names.append(name)

            display_name = default_name or namespace_alias or module
            imp = ImportDef(
                name=display_name,
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                names=names,
                is_from_import=True,
                metadata={"default": default_name, "namespace": namespace_alias},
            )
            imports.append(imp)

        # CommonJS require
        require_pattern = re.compile(
            r"(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        )

        for match in require_pattern.finditer(cleaned_source):
            name = match.group(1)
            module = match.group(2)
            line_num = cleaned_source[:match.start()].count("\n") + 1

            imp = ImportDef(
                name=name,
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                alias=name,
                is_from_import=False,
                metadata={"style": "commonjs"},
            )
            imports.append(imp)

        return imports

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """解析 JavaScript/TypeScript 变量定义

        匹配模式：
        - const/let/var NAME = value
        """
        variables: List[VariableDef] = []

        pattern = re.compile(
            r"^(?:const|let|var)\s+([A-Z_][A-Z0-9_]*)\s*(?::\s*([^\n=]+))?\s*=\s*(.+)$",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            var_type = (match.group(2) or "").strip()
            value = match.group(3).strip()[:50]
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
        func_pattern = re.compile(
            r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)"
        )
        func_names = set()
        for match in func_pattern.finditer(cleaned_source):
            name = match.group(1) or match.group(2)
            if name:
                func_names.add(name)

        # 查找函数调用
        call_pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")

        for caller in func_names:
            # 查找函数体
            caller_match = re.search(
                r"(?:function\s+|(?:const|let|var)\s+" + re.escape(caller) + r"\s*=)"
                r".*?\{",
                cleaned_source,
            )
            if not caller_match:
                continue

            body_start = caller_match.end() - 1
            body_end = self._find_block_end_pos(cleaned_source, body_start)
            body = cleaned_source[body_start:body_end]

            seen = set()
            for call_match in call_pattern.finditer(body):
                callee = call_match.group(1)
                if callee in _JS_BUILTINS or callee in seen:
                    continue
                seen.add(callee)
                line_num = cleaned_source[:body_start + call_match.start()].count("\n") + 1
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
            name = param.split(":")[0].split("=")[0].strip()
            if name:
                params.append(name)
        return params

    def _find_block_end(self, source: str, open_brace: int) -> int:
        """查找花括号块的结束行号"""
        end_pos = self._find_block_end_pos(source, open_brace)
        return source[:end_pos].count("\n") + 1

    def _find_block_end_pos(self, source: str, open_brace: int) -> int:
        """查找花括号块的结束位置"""
        depth = 0
        in_string = False
        string_char = ""
        i = open_brace
        while i < len(source):
            ch = source[i]
            if in_string:
                if ch == "\\" and i + 1 < len(source):
                    i += 2
                    continue
                if ch == string_char:
                    in_string = False
            else:
                if ch in ('"', "'", "`"):
                    in_string = True
                    string_char = ch
                elif ch == "{":
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
            if name not in _JS_BUILTINS and name not in seen:
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
            (r"\bwhile\b", 1),
            (r"\bcase\b", 1),
            (r"\bcatch\b", 1),
            (r"\&\&", 1),
            (r"\|\|", 1),
            (r"\?\?", 1),
            (r"\?", 1),  # 三元运算符
        ]
        for pattern_str, weight in branch_patterns:
            matches = re.findall(pattern_str, body)
            complexity += len(matches) * weight
        return complexity


# JavaScript 内置对象/函数
_JS_BUILTINS = {
    "console", "Math", "JSON", "Object", "Array", "String", "Number",
    "Boolean", "Date", "RegExp", "Error", "Map", "Set", "WeakMap", "WeakSet",
    "Promise", "Symbol", "Proxy", "Reflect", "parseInt", "parseFloat",
    "isNaN", "isFinite", "encodeURI", "decodeURI", "encodeURIComponent",
    "decodeURIComponent", "setTimeout", "setInterval", "clearTimeout",
    "clearInterval", "requestAnimationFrame", "fetch", "require", "module",
    "exports", "process", "Buffer", "global", "window", "document",
    "alert", "confirm", "true", "false", "null", "undefined", "this",
    "super", "new", "delete", "typeof", "instanceof", "void",
}
