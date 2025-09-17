from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as fh:
    license_text = fh.read()

setup(
    name="ai-elderly-medicare-system",
    version="1.0.0",
    author="AI Medicare Team",
    author_email="support@ai-medicare-system.com",
    description="A comprehensive healthcare management system for elderly patients with AI-powered features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/ai-elderly-medicare-system",
    license=license_text,
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "alembic>=1.7.0",
        "pydantic>=1.8.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.5",
        "email-validator>=1.1.3",
        "celery>=5.1.0",
        "redis>=3.5.3",
        "requests>=2.25.1",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "tensorflow>=2.6.0",
        "openai>=0.27.0",
        "twilio>=7.0.0",
        "python-dotenv>=0.19.0",
        "pydantic[dotenv]>=1.8.0",
        "streamlit>=1.0.0",
        "plotly>=5.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    extras_require={
        "dev": [
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "medicare-run=app.main:main",
            "medicare-init=scripts.setup_database:main",
            "medicare-seed=scripts.seed_data:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)