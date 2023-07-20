from setuptools import setup

setup(
    version="0.1",
    name="AGBM Client",
    description="GeekBrains Study Project Client",
    author="Makutu",
    author_email="makutu@ereb.ru",
    packages=["config", "common", "db", "log", "client_gui", "client"],
    install_requires=[
        "typer>=0.9.0",
        "pydantic>=1.10.8",
        "pytest>=7.3.1",
        "rich>=13.4.1",
        "chardet>=5.1.0",
        "ipaddress>=1.0.23",
        "tabulate>=0.9.0",
        "SQLAlchemy>=2.0.17",
        "alembic>=1.11.1",
        "PyQt6>=6.5.1",
        "configparser>=5.3.0",
        "bcrypt>=4.0.1",
        "Flake8-pyproject>=1.2.3",
        "sphinx>=7.0.1",
    ],
)
