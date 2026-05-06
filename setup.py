import os
from setuptools import setup, find_packages

def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="openbro",
    version="1.0",
    packages=find_packages(),
    author="Lazarus Rolando",
    description="A simple framework for training and deploying language models.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires=["rich", "requests", "click"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "openbro=openbro.cli:cli"
        ]
    },
)