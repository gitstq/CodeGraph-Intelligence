"""
Java 代码解析器

使用正则表达式解析 Java 源代码，提取类、接口、方法、导入和调用关系。
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


class JavaParser(BaseParser):
    """Java 代码解析器"""

    language = "java"
    extensions = [".java"]

    def __init__(self):
        super().__init__()
        # Java 注释模式
        self.comment_patterns = [
            re.compile(r"/\*[\s\S]*?\*/"),  # 多行注释
            re.compile(r"//.*$"),  # 单行注释
        ]
        # Java 字符串模式
        self.string_pattern = re.compile(
            r'"(?:[^"\\]|\\.)*"',
        )

    def parse_functions(
        self, cleaned_source: str, raw_source: str
    ) -> List[FunctionDef]:
        """解析 Java 方法定义

        匹配模式：
        - public/private/protected static void name(params) { }
        - public ReturnType name(params) throws Exception { }
        - @Override public void name(params) { }
        """
        functions: List[FunctionDef] = []

        pattern = re.compile(
            r"(?:@\w+\s+)*"
            r"(?:public|private|protected)\s+"
            r"(?:static\s+)?"
            r"(?:final\s+)?"
            r"(?:synchronized\s+)?"
            r"([\w<>\[\],\s]+?)\s+"  # 返回类型
            r"(\w+)\s*"  # 方法名
            r"\(([^)]*)\)"  # 参数
            r"(?:\s+throws\s+[^{]+)?"  # throws 子句
            r"\s*\{",
        )

        for match in pattern.finditer(cleaned_source):
            return_type = match.group(1).strip()
            name = match.group(2)
            params_str = match.group(3).strip()
            line_start = cleaned_source[:match.start()].count("\n") + 1

            # 过滤掉类定义（返回类型中包含 class/interface/enum）
            if return_type in ("class", "interface", "enum"):
                continue

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
        """解析 Java 类、接口和枚举定义

        匹配模式：
        - public class Name { }
        - public class Name extends Base implements Interface { }
        - public interface Name { }
        - public enum Name { }
        """
        classes: List[ClassDef] = []

        # 类定义
        class_pattern = re.compile(
            r"(?:public|private|protected)?\s*(?:abstract\s+)?(?:final\s+)?"
            r"class\s+(\w+)"
            r"(?:<[^>]*>)?"
            r"(?:\s+extends\s+([\w.<>,\s]+?))?"
            r"(?:\s+implements\s+([\w.<>,\s]+?))?"
            r"\s*\{",
        )

        for match in class_pattern.finditer(cleaned_source):
            name = match.group(1)
            extends = match.group(2) or ""
            implements = match.group(3) or ""
            line_start = cleaned_source[:match.start()].count("\n") + 1

            bases = []
            if extends:
                bases.extend([b.strip() for b in extends.split(",") if b.strip()])
            if implements:
                bases.extend([b.strip() for b in implements.split(",") if b.strip()])

            class_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(
                r"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],\s]+?\s+(\w+)\s*\(",
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
                metadata={"kind": "class"},
            )
            classes.append(cls)

        # 接口定义
        interface_pattern = re.compile(
            r"(?:public|private|protected)?\s*interface\s+(\w+)"
            r"(?:<[^>]*>)?"
            r"(?:\s+extends\s+([\w.<>,\s]+?))?"
            r"\s*\{",
        )

        for match in interface_pattern.finditer(cleaned_source):
            name = match.group(1)
            extends = match.group(2) or ""
            line_start = cleaned_source[:match.start()].count("\n") + 1

            bases = [b.strip() for b in extends.split(",") if b.strip()] if extends else []

            iface_body = self._extract_block_body(cleaned_source, match.end() - 1)
            methods = re.findall(r"([\w<>\[\],\s]+?)\s+(\w+)\s*\(", iface_body)

            line_end = self._find_block_end(cleaned_source, match.end() - 1)

            cls = ClassDef(
                name=name,
                element_type="class",
                line_start=line_start,
                line_end=line_end,
                bases=bases,
                methods=methods,
                metadata={"kind": "interface"},
            )
            classes.append(cls)

        # 枚举定义
        enum_pattern = re.compile(
            r"(?:public|private|protected)?\s*enum\s+(\w+)"
            r"(?:<[^>]*>)?"
            r"(?:\s+implements\s+([\w.<>,\s]+?))?"
            r"\s*\{",
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

        return classes

    def parse_imports(self, cleaned_source: str) -> List[ImportDef]:
        """解析 Java 导入语句

        匹配模式：
        - import package.Class;
        - import package.*;
        - import static package.Class.method;
        """
        imports: List[ImportDef] = []

        pattern = re.compile(
            r"import\s+(static\s+)?([\w.]+(?:\.\*)?)\s*;",
        )

        for match in pattern.finditer(cleaned_source):
            is_static = bool(match.group(1))
            module = match.group(2)
            line_num = cleaned_source[:match.start()].count("\n") + 1

            names = []
            if module.endswith(".*"):
                names = ["*"]
            else:
                names = [module.split(".")[-1]]

            imp = ImportDef(
                name=module,
                element_type="import",
                line_start=line_num,
                line_end=line_num,
                module=module,
                names=names,
                is_from_import=True,
                metadata={"is_static": is_static},
            )
            imports.append(imp)

        return imports

    def parse_variables(self, cleaned_source: str) -> List[VariableDef]:
        """解析 Java 变量定义

        匹配模式：
        - public static final Type NAME = value;
        - private static final Type NAME = value;
        """
        variables: List[VariableDef] = []

        pattern = re.compile(
            r"(?:public|private|protected)\s+static\s+final\s+"
            r"([\w<>\[\]]+)\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);",
            re.MULTILINE,
        )

        for match in pattern.finditer(cleaned_source):
            var_type = match.group(1).strip()
            name = match.group(2)
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

        # 找到所有方法定义
        func_pattern = re.compile(
            r"(?:public|private|protected)\s+(?:static\s+)?"
            r"(?:final\s+)?[\w<>\[\],\s]+?\s+(\w+)\s*\([^)]*\)"
            r"(?:\s+throws\s+[^{]+)?\s*\{",
        )
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
                if callee in _JAVA_BUILTINS or callee in seen:
                    continue
                seen.add(callee)
                line_num = cleaned_source[:start + call_match.start()].count("\n") + 1
                calls.append((caller, callee, line_num))

        return calls

    # ── 私有辅助方法 ──

    def _parse_parameters(self, params_str: str) -> List[str]:
        """解析 Java 方法参数"""
        if not params_str:
            return []
        params = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue
            # Java 参数格式: Type name 或 final Type name
            parts = param.split()
            if len(parts) >= 2:
                params.append(parts[-1])  # 最后一个 token 是参数名
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
        """从方法体中提取被调用的函数名"""
        calls = []
        pattern = re.compile(r"(\w+(?:\.\w+)*)\s*\(")
        seen = set()
        for match in pattern.finditer(body):
            name = match.group(1)
            if name not in _JAVA_BUILTINS and name not in seen:
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
        ]
        for pattern_str, weight in branch_patterns:
            matches = re.findall(pattern_str, body)
            complexity += len(matches) * weight
        return complexity


_JAVA_BUILTINS = {
    "System", "String", "Integer", "Long", "Double", "Float", "Boolean",
    "Character", "Byte", "Short", "Object", "Class", "Thread", "Runnable",
    "Exception", "RuntimeException", "List", "ArrayList", "Map", "HashMap",
    "Set", "HashSet", "Queue", "LinkedList", "Arrays", "Collections",
    "Math", "Scanner", "File", "IOException", "println", "print",
    "printf", "valueOf", "parseInt", "parseLong", "toString", "equals",
    "hashCode", "getClass", "notify", "notifyAll", "wait", "clone",
    "finalize", "this", "super", "new", "return", "null", "true", "false",
    "instanceof", "override", "final", "static", "abstract", "synchronized",
}
