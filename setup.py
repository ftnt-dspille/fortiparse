"""
Setup script for FortiParse.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fortiparse",
    version="0.1.0",
    author="Dylan Spille",
    author_email="dspille@fortinet.com",
    description="A Python library to parse FortiGate configuration files into JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fortiparse",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
