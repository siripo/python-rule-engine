import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='siripo-rule-engine',
    version='0.1',
    scripts=['siripo-rule-engine'],
    author="Mariano Augusto Santamarina",
    author_email="msantamarina@gmail.com",
    description="Simple and powerful rule engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/siripo/python-rule-engine",
    packages=["siripo.rule_engine"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
)
