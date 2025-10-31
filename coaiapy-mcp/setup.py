"""
Setup script for coaiapy-mcp package.

For modern Python packaging, see pyproject.toml.
This setup.py is provided for compatibility.
"""
from setuptools import setup, find_packages

setup(
    packages=find_packages(exclude=["tests*"]),
    package_data={
        "coaiapy_mcp": ["*.json", "*.txt"],
    },
)
