"""
Setup script for coaiapy-mcp package
"""

from setuptools import setup, find_packages

setup(
    name="coaiapy-mcp",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "coaiapy>=0.2.54",
        "mcp>=0.1.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "coaiapy-mcp=coaiapy_mcp.server:cli_main",
        ],
    },
    author="Jean Guillaume Isabelle",
    author_email="jgi@jgwill.com",
    description="MCP (Model Context Protocol) wrapper for coaiapy observability toolkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jgwill/coaiapy",
    project_urls={
        "Documentation": "https://github.com/jgwill/coaiapy/tree/main/coaiapy-mcp",
        "Source": "https://github.com/jgwill/coaiapy",
        "Issues": "https://github.com/jgwill/coaiapy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
