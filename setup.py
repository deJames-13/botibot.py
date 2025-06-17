#!/usr/bin/env python3
"""
Setup script for botibot package.

A python package for Project Botibot
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md for long description."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A python package for Project Botibot"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "adafruit-circuitpython-ssd1306",
            "adafruit-blinka",
            "Pillow",
            "RPi.GPIO",
            "Flask",
            "Flask-CORS",
            "python-dateutil"
        ]

setup(
    name="botibot.py",
    version="1.0.0",
    author="deJames-13",
    author_email="de.james013@gmail.com",
    description="A python package for Project Botibot",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/deJames-13/botibot",
    project_urls={
        "Bug Tracker": "https://github.com/deJames-13/botibot/issues",
        "Documentation": "https://github.com/deJames-13/botibot/blob/main/README.md",
        "Source Code": "https://github.com/deJames-13/botibot",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Other Environment",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
        "full": [
            "matplotlib",
            "numpy",
            "scipy",
        ],
    },
    entry_points={
        "console_scripts": [
            "botibot-demo=modules.cli:main",
            "botibot-servo=modules.cli:servo_cli",
            "botibot-oled=modules.cli:oled_cli",
            "botibot-relay=modules.cli:relay_cli",
            "botibot-server=modules.cli:server_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "modules": [
            "*.md",
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    zip_safe=False,
    keywords=[
        "botibot.py",
        "botibot",
        "raspberry-pi",
        "microcontroller",
        "servo",
        "oled",
        "relay",
        "gpio",
        "iot",
        "embedded",
        "hardware",
        "automation",
        "robotics",
        "project",
    ],
    platforms=["Linux"],
)
