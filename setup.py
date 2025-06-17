from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A smart recipe assistant that finds recipes based on available ingredients"

def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="recipe-assistant",
    version="1.0.0",
    description="A smart recipe assistant that finds recipes based on available ingredients",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/recipe-assistant",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/recipe-assistant/issues",
        "Source": "https://github.com/yourusername/recipe-assistant",
        "Documentation": "https://github.com/yourusername/recipe-assistant/wiki",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    keywords="recipe, cooking, food, ingredients, meal-planning, nutrition",
    entry_points={
        "console_scripts": [
            "recipe-assistant=src.recipe_assistant:main",
            "recipe-web=app:app.run",
        ],
    },
    package_data={
        "": ["*.txt", "*.md", "*.json"],
        "data": ["*.json"],
        "templates": ["*.html"],
        "static": ["*"],
    },
    exclude_package_data={
        "": ["*.pyc", "__pycache__", "*.pyo"],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
        "web": [
            "flask>=2.3.0",
            "flask-sqlalchemy>=3.0.0",
            "pillow>=10.0.0",
        ],
        "api": [
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
        ],
    },
    license="MIT",
    zip_safe=False,
)