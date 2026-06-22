"""
setup.py - Project setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().split("\n")
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="jj-assistant",
    version="0.1.0",
    author="Asghar Ali",
    author_email="asghar778788@example.com",
    description="JJ - A JARVIS-inspired personalized AI voice assistant with persistent memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asghar4415/JJ_Assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Speech Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jj=src.main:main",
        ],
    },
    include_package_data=True,
)
