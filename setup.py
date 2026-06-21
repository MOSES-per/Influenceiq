from setuptools import setup, find_packages

setup(
    name="influenceiq",
    version="1.0.0",
    description="Cross-platform influencer intelligence and analytics engine",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pandas",
        "streamlit",
        "matplotlib",
        "reportlab"
    ],
    python_requires=">=3.8"
)
