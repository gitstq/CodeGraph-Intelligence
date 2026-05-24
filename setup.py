#!/usr/bin/env python
"""CodeGraph-Lite 安装脚本"""

from setuptools import setup, find_packages

setup(
    name="codegraph-lite",
    version="0.1.0",
    description="轻量级代码知识图谱智能分析引擎 - 纯Python标准库实现",
    long_description=open("README.md", encoding="utf-8").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="CodeGraph-Lite Contributors",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(include=["codegraph_lite*"]),
    entry_points={
        "console_scripts": [
            "codegraph=codegraph_lite.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
