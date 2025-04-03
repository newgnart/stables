from setuptools import setup, find_packages

setup(
    name="stables",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "python-dotenv",
        "aiohttp",
        "psycopg2-binary",
    ],
    python_requires=">=3.9",
)
