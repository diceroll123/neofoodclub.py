from setuptools import setup
import contextlib
import re

version = ''
with open('neofoodclub/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

if version.endswith(("a", "b", "rc")):
    # append version identifier based on commit count
    with contextlib.suppress(Exception):
        import subprocess

        p = subprocess.Popen(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="neofoodclub.py",
    author="diceroll123",
    url="https://github.com/diceroll123/neofoodclub.py",
    version=version,
    license="MIT",
    description="A Python implementation of functionality used in https://neofood.club",
    python_requires=">=3.7",
    packages=["neofoodclub"],
    install_requires=requirements,
)
