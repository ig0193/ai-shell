from setuptools import setup, find_packages

setup(
    name="ai-shell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "litellm",
        "rich",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "ai=ai_shell.cli:entry",
        ],
    },
    python_requires=">=3.9",
)
