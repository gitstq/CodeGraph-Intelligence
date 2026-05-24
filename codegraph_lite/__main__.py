"""
CodeGraph-Lite CLI 入口模块

提供命令行接口的入口点，解析用户命令并分发到对应的功能模块。
"""

import sys
from .cli import parse_args, run_command


def main() -> None:
    """CLI 主入口函数"""
    args = parse_args()
    try:
        run_command(args)
    except KeyboardInterrupt:
        print("\n操作已取消。")
        sys.exit(130)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
