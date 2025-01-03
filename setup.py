from setuptools import setup, find_packages
print("Detected packages:", find_packages())

setup(
    name="ai-reviewer",
    version="1.0.0",
    description="AI code reviewer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Bouziane Amine",
    url="https://github.com/BouzianeAminePro/ai-reviewer",
    packages=find_packages(),
    install_requires=[
        "langchain_ollama",
    ],
    entry_points={
        "console_scripts": [
            "aiview=aiview.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
