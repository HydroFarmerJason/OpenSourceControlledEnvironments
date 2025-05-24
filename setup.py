"""
Setup configuration for OpenSourceControlledEnvironments
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opensourcecontrolledenvironments",
    version="1.0.0",
    author="HydroFarmerJason",
    author_email="",
    description="Open source controlled environment agriculture system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=[
        # List core requirements here
        # Full list in requirements.txt
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "farm-controller=farm.cli:main",
            "farm-api=farm.api:run_server",
        ],
    },
)

