import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AuthoritySpoke",
    version="0.1.0",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="tool for managing structured data about legal authority",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mscarey/AuthoritySpoke",
    packages=setuptools.find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=["beautifulsoup4", "lxml", "pint", "requests", "ipykernel"],
    extras_require={"jupyter notebooks": "jupyter"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Sociology :: History",
    ],
    include_package_data=True,
)
