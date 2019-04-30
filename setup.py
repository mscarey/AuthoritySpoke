import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AuthoritySpoke",
    version="0.0.1",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="a tool for constructing data about legal rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mscarey/AuthoritySpoke",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Sociology :: History",
    ],
)