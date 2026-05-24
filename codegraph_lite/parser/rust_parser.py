"""
Rust 代码解析器

使用正则表达式解析 Rust 源代码，提取函数、结构体、枚举、trait、导入和调用关系。
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


class RustParser(BaseParser):
    """Rust 代码解析器"""

    language = "rust"
    extensions = [".rs"]

    def __init__(self):
        super().__init__()
        # Rust 注释模式
        self.comment_patterns = [
            re.compile(r"/\*[\s\S]*?\*/"),  # 多行注释
            re.compile(r"//.*$"),  # 单行注释
            re.compile(r"///.*$"),  # 文档注释
            re.compile(r"//!.*$"),  # 内部文档注释
        ]
        # Rust 字符串模式
        self.string_pattern = re.compile(
            r'"(?:[^"\\]|\\.)*"|r#*"[^"]*"#*|\'(?:[^\'\\]|\\.)*\'',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析 Rust 函数定义

        匹配模式：
        - fn name(params) -> ReturnType { }
        - pub fn name(params) -> ReturnType { }
        - pub async fn name(params) -> ReturnType { }
        - fn name(params) where ... { }
        """
        functions: List[FunctionDef] = []

        pattern = re.compile(
            r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*<[^>]*>\s*\(([^)]*)\)"
            r"(?:\s*->\s*([^{]+))?\s*(?:where\s+[^{]+)?\s*\{",
        )

        # 也匹配不带泛型的函数
        pattern2 = re.compile(
            r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)"
            r"(?:\s*->\s*([^{]+))?\s*(?:where\s+[^{]+)?\s*\{",
        )

        seen = set()
        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            self._add_function(functions, match, cleaned_source)

        for match in pattern2.finditer(cleaned_source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            self._add_function(functions, match, cleaned_source)

        return functions

    def _add_function(
        self, functions: List[FunctionDef], match: re.Match, source: str
    ) -> None:
        """辅助方法：添加函数定义"""
        name = match.group(1)
        params_str = match.group(2).strip()
        return_type = (match.group(3) or "").strip()
        line_start = source[:match.start()].count("\n") + 1

        parameters = self._parse_parameters(params_str)
        line_end = self._find_block_end(source, match.end() - 1)
        func_body = self._extract_block_body(source, match.end() - 1)
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

    def parse_classes(
        self, cleaned_source: str, raw_source: str
    ) -> List[ClassDef]:
        """解析 Rust 结构体、枚举和 trait

        匹配模式：
        - struct Name { }
        - struct Name(Type1, Type2)
        - enum Name { }
        - trait Name { }
        - impl Name { }
        """
        classes: List[ClassDef] = []

        # 结构体
        struct_pattern = re.compile(
            r"(?:pub\s+)?struct\s+(\w+)(?:<[^>]*>)?\s*(?:\([^)]*\)|\{)",
        )
        for match in struct_pattern.finditer(cleaned_source):
            name = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                metadata={"kind": "struct"},
            )
            classes.append(cls)

        # 枚举
        enum_pattern = re.compile(
            r"(?:pub\s+)?enum\s+(\w+)(?:<[^>]*>)?\s*\{",
        )
        for match in enum_pattern.finditer(cleaned_source):
            name = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                metadata={"kind": "enum"},
            )
            classes.append(cls)

        # trait
        trait_pattern = re.compile(
            r"(?:pub\s+)?trait\s+(\w+)(?:<[^>]*>)?\s*(?:\s*:\s*[^{]+)?\s*\{",
        )
        for match in trait_pattern.finditer(cleaned_source):
            name = match.group(1)
            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            bases_str = ""
            bases_match = re.search(
                r"trait\s+\w+(?:<[^>]*>)?\s*:\s*([^{]+)", match.group(0)
            )
            if bases_match:
                bases_str = bases_match.group(1)
            bases = [b.strip() for b in bases_str.split("+") if b.strip()]

            trait_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(r"fn\s+(\w+)\s*\(", trait_body)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                bases=bases,
                methods=methods,
                metadata={"kind": "trait"},
            )
            classes.append(cls)

        # impl 块（提取方法）
        impl_pattern = re.compile(
            r"impl(?:<[^>]*>)?\s+(\w+)(?:<[^>]*>)?\s*(?:\s+for\s+\w+(?:<[^>]*>)?)?\s*\{",
        )
        for match in impl_pattern.finditer(cleaned_source):
            name = match.group(1)
            impl_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(r"fn\s+(\w+)\s*\(", impl_body)

            line_start = cleaned_source[:match.start()].count("\n") + 1
            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                methods=methods,
                metadata={"kind": "impl"},
            )
            classes.append(cls)

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析 Rust 导入语句

        匹配模式：
        - use module::name;
        - use module::{name1, name2};
        - use module::name as alias;
        """
        imports: List[ImportDef] = []

        # use 语句
        pattern = re.compile(
            r"use\s+([\w:]+)(?:::\{([^}]+)\})?(?:\s+as\s+(\w+))?\s*;",
        )

        for match in pattern.finditer(cleaned_source):
            module = match.group(1)
            names_str = match.group(2) or ""
            alias = match.group(3) or ""
            line_num = cleaned_source[:match.start()].count("\n") + 1

            names = []
            if names_str:
                for name in names_str.split(","):
                    name = name.strip()
                    if name:
                        if " as " in name:
                            names.append(name)
                        else:
                            names.append(name)

            display_name = alias or module.split("::")[-1]
            imp = ImportDef(
                name=display_name,
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                alias=alias,
                names=names,
                is_from_import=True,
            )
            imports.append(imp)

        return imports

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """解析 Rust 变量定义

        匹配模式：
        - const NAME: type = value;
        - static NAME: type = value;
        """
        variables: List[VariableDef] = []

        pattern = re.compile(
            r"(?:pub\s+)?(?:const|static)\s+([A-Z_][A-Z0-9_]*)\s*:\s*([^{;]+?)\s*=\s*([^;]+);",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            name = match.group(1)
            var_type = match.group(2).strip()
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

        func_pattern = re.compile(r"fn\s+(\w+)\s*<[^>]*>\s*\(|fn\s+(\w+)\s*\(")
        func_ranges: List[Tuple[str, int, int]] = []
        seen_names = set()
        for match in func_pattern.finditer(cleaned_source):
            name = match.group(1) or match.group(2)
            if name and name not in seen_names:
                seen_names.add(name)
                start = match.start()
                # 找到函数体
                brace_pos = cleaned_source.find("{", match.end())
                if brace_pos == -1:
                    continue
                end = self._find_block_end_pos(cleaned_source, brace_pos)
                func_ranges.append((name, start, end))

        call_pattern = re.compile(r"(\w+(?:::\w+)*)\s*(?:<[^>]*>)?\s*\(")

        for caller, start, end in func_ranges:
            body = cleaned_source[start:end]
            seen = set()
            for call_match in call_pattern.finditer(body):
                callee = call_match.group(1)
                if callee in _RUST_BUILTINS or callee in seen:
                    continue
                seen.add(callee)
                line_num = cleaned_source[:start + call_match.start()].count("\n") + 1
                calls.append((caller, callee, line_num))

        return calls

    # ── 私有辅助方法 ──

    def _parse_parameters(self, params_str: str) -> List[str]:
        """解析 Rust 函数参数"""
        if not params_str:
            return []
        params = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue
            # Rust 参数格式: name: type 或 self 或 &self 或 mut self
            parts = param.split(":")
            name = parts[0].strip()
            if name and name not in ("self", "&self", "&mut self", "mut self"):
                params.append(name)
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
        pattern = re.compile(r"(\w+(?:::\w+)*)\s*(?:<[^>]*>)?\s*\(")
        seen = set()
        for match in pattern.finditer(body):
            name = match.group(1)
            if name not in _RUST_BUILTINS and name not in seen:
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
            (r"\bloop\b", 1),
            (r"\bmatch\b", 1),
            (r"\&\&", 1),
            (r"\|\|", 1),
            (r"\?", 1),  # ? 运算符
        ]
        for pattern_str, weight in branch_patterns:
            matches = re.findall(pattern_str, body)
            complexity += len(matches) * weight
        return complexity


_RUST_BUILTINS = {
    "println", "eprintln", "print", "eprint", "format", "vec", "panic",
    "assert", "assert_eq", "assert_ne", "todo", "unimplemented", "unreachable",
    "dbg", "some", "none", "ok", "err", "true", "false", "self", "super",
    "Self", "Box", "Vec", "String", "Option", "Result", "HashMap", "HashSet",
    "Rc", "Arc", "Mutex", "RwLock", "Cow", "PhantomData",
}
