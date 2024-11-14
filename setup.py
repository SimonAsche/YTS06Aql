from setuptools import setup, find_packages

setup(
    name="youtube_playlist",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.41.0",
        "agentql>=0.5.0",
        "pandas>=2.1.4",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.2",
        "openpyxl>=3.1.2",
    ],
    extras_require={
        'dev': [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "pytest-asyncio>=0.23.0",
        ]
    }
) 