import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AuthoritySpoke",
    version="0.8.0",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="legal authority automation",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mscarey/authorityspoke",
    project_urls={
        "Bug Tracker": "https://github.com/mscarey/authorityspoke/issues",
        "Documentation": "https://authorityspoke.readthedocs.io/en/latest/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "License :: Free To Use But Restricted",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "anchorpoint~=0.5.2",
        "apispec[validation]~=4.3.0",
        "apispec-oneofschema",
        "eyecite~=2.2.0",
        "justopinion~=0.2.3",
        "legislice>=0.5.2",
        "marshmallow>=3.10",
        "marshmallow-oneofschema",
        "nettlesome>=0.5.1",
        "pint>=0.15",
        "pydantic",
        "python-dotenv",
        "python-slugify",
        "pyyaml",
        "requests",
        "roman",
        "sympy>=1.7.1",
    ],
    python_requires=">=3.8",
)
