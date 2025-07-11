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
            return [
                line.strip() for line in fh if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return [
            "adafruit-circuitpython-ssd1306",
            "adafruit-blinka",
            "Pillow",
            "RPi.GPIO",
            "gpiozero",
            "Flask",
            "Flask-CORS",
            "python-dateutil",
            "adafruit-circuitpython-mlx90614",
            "pyserial",
            "schedule",
            "apscheduler",
        ]


setup(
    name="botibot.py",
    version="1.0.6",
    author="deJames-13",
    author_email="de.james013@gmail.com",
    description="A python package for Project Botibot with gpiozero integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/deJames-13/botibot.py",
    project_urls={
        "Bug Tracker": "https://github.com/deJames-13/botibot.py/issues",
        "Documentation": "https://github.com/deJames-13/botibot.py/blob/main/README.md",
        "Source Code": "https://github.com/deJames-13/botibot.py",
    },
    packages=find_packages(include=["botibot", "botibot.*"]),
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
            "botibot-demo=botibot.cli:main",
            "botibot-servo=botibot.cli:servo_cli_entry",
            "botibot-oled=botibot.cli:oled_cli_entry",
            "botibot-relay=botibot.cli:relay_cli_entry",
            "botibot-server=botibot.cli:server_cli_entry",
            "botibot-gsm=botibot.gsm.cli:main",
            "botibot-ir-temp=botibot.cli:ir_temp_cli_entry",
            "botibot-scheduler=botibot.scheduler.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "botibot": [
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
        "modules",
        "raspberry-pi",
        "microcontroller",
        "servo",
        "oled",
        "relay",
        "infrared",
        "ultrasonic",
        "motor",
        "gpio",
        "gpiozero",
        "iot",
        "embedded",
        "hardware",
        "automation",
        "robotics",
        "project",
    ],
    platforms=["Linux"],
)
