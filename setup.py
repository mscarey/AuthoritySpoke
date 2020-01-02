import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AuthoritySpoke",
    version="0.3.4",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="tool for managing structured data about legal authority",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mscarey/AuthoritySpoke",
    packages=setuptools.find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=[
        "anchorpoint",
        "apispec",
        "beautifulsoup4",
        "lxml",
        "marshmallow",
        "pint",
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "License :: Free To Use But Restricted",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Sociology :: History",
    ],
    python_requires=">=3.7, <3.8",
    include_package_data=True,
)
