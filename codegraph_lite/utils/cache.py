"""
增量缓存模块

使用 JSON 文件存储文件解析缓存，支持增量索引。
基于文件修改时间判断是否需要重新解析。
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional


class FileCache:
    """文件解析缓存

    使用 JSON 文件存储每个文件的解析摘要和修改时间。
    当文件未修改时直接使用缓存结果，避免重复解析。
    """

    def __init__(self, project_path: str, cache_dir: str = ".codegraph_cache"):
        """初始化缓存

        Args:
            project_path: 项目根目录路径
            cache_dir: 缓存目录名称
        """
        self.cache_dir = os.path.join(project_path, cache_dir)
        self.cache_file = os.path.join(self.cache_dir, "cache.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._dirty = False

        # 加载已有缓存
        self._load()

    def get(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件的缓存数据

        Args:
            file_path: 文件路径

        Returns:
            缓存的解析摘要，如果缓存无效返回 None
        """
        abs_path = os.path.abspath(file_path)

        if abs_path not in self._cache:
            return None

        cached = self._cache[abs_path]

        # 检查文件修改时间
        try:
            mtime = os.path.getmtime(abs_path)
            if cached.get("mtime", 0) >= mtime:
                return cached.get("data")
        except OSError:
            pass

        # 缓存过期，删除
        del self._cache[abs_path]
        self._dirty = True
        return None

    def set(self, file_path: str, data: Dict[str, Any]) -> None:
        """设置文件缓存数据

        Args:
            file_path: 文件路径
            data: 解析摘要数据
        """
        abs_path = os.path.abspath(file_path)

        try:
            mtime = os.path.getmtime(abs_path)
        except OSError:
            mtime = time.time()

        self._cache[abs_path] = {
            "mtime": mtime,
            "data": data,
        }
        self._dirty = True

    def invalidate(self, file_path: str) -> None:
        """使指定文件的缓存失效

        Args:
            file_path: 文件路径
        """
        abs_path = os.path.abspath(file_path)
        if abs_path in self._cache:
            del self._cache[abs_path]
            self._dirty = True

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache = {}
        self._dirty = True
        self._save()

    def save(self) -> None:
        """保存缓存到磁盘"""
        if self._dirty:
            self._save()

    def _load(self) -> None:
        """从磁盘加载缓存"""
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            self._cache = {}

    def _save(self) -> None:
        """保存缓存到磁盘"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
            self._dirty = False
        except (IOError, OSError):
            pass

    def __del__(self):
        """析构时自动保存缓存"""
        if self._dirty:
            self._save()
