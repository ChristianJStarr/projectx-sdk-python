"""Setup script for the ProjectX SDK package."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies
install_requires = [
    "requests>=2.25.0",
    "signalrcore==0.9.2",
    "python-dateutil>=2.8.2",
    "websocket-client==0.54.0",
    "pydantic>=2.0.0",
]

# Test dependencies
test_requires = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "responses>=0.22.0",
    "pytest-mock>=3.10.0",
]

# Development dependencies
dev_requires = [
    "black>=23.1.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "sphinx>=5.3.0",
    "sphinx-rtd-theme>=1.2.0",
    "pre-commit>=3.0.0",
    "twine>=4.0.0",
    "build>=0.10.0",
] + test_requires

setup(
    name="projectx-sdk",
    version="0.1.0",
    author="ProjectX Team",
    author_email="info@projectx.com",
    description="Python SDK for the ProjectX Gateway API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChristianJStarr/projectx-sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/ChristianJStarr/projectx-sdk-python/issues",
        "Documentation": "https://projectx-sdk-python.readthedocs.io/",
        "Source Code": "https://github.com/ChristianJStarr/projectx-sdk-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "test": test_requires,
        "dev": dev_requires,
    },
)
