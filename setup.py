import os
import re
import setuptools

with open("README.md", mode="r") as file:
    long_description = file.read()
    
with open(
    os.path.join(os.path.join(os.path.dirname(__file__), "redutils"), "version.py"), mode="r"
) as file:
    content = file.read()
    
__version__ = float(
    re.compile(r"__version__\s*=\s*(?P<version>\d+\.\d+)").search(content).groupdict()["version"] # type: ignore
)

setuptools.setup(
    name="redutils",
    version=str(__version__),
    author="japandotorg [inthedark.org]",
    author_email="japandotorg@pm.me",
    description="Utils for Red-Discord Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/japandotorg/redutils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.1",
    install_requires=[
        "fuzzywuzzy"
    ],
)
