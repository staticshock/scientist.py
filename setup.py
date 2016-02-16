#!/usr/bin/env python
from setuptools import setup

setup(
    name='scientist',
    version='0.1.0',
    description="Scientist: Take a scalpel to your critical paths",
    long_description=open("README.rst").read(),
    author="Anton Backer",
    author_email="olegov@gmail.com",
    url="http://www.github.com/staticshock/scientist.py",
    packages=['scientist'],
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
    )
)
