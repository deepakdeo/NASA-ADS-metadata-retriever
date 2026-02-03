"""
Setup configuration for NASA ADS metadata retriever package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="nasa-ads-metadata-retriever",
    version="2.0.0",
    author="Deepak Deo",
    author_email="deepak@example.com",
    description="Query and export astronomy paper metadata from NASA ADS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deepakdeo/NASA-ADS-metadata-retriever",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nasa-ads-finder=nasa_ads.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
