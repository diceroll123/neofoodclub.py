import contextlib
import re

from setuptools import setup
from setuptools_rust import Binding, RustExtension

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ""
with open("neofoodclub/__init__.py") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    )

if not version:
    raise RuntimeError("version is not set")
else:
    version = version[1]

packages = [
    "neofoodclub",
    "neofoodclub.types",
]

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


setup(
    name="neofoodclub.py",
    author="diceroll123",
    description="A Python implementation of functionality used in https://neofood.club",
    license="MIT",
    license_file="LICENSE",
    url="https://github.com/diceroll123/neofoodclub.py",
    version=version,
    packages=packages,
    rust_extensions=[RustExtension("neofoodclub.neofoodclub", binding=Binding.PyO3)],
    python_requires=">=3.8.0",
    classifiers=[
        "Programming Language :: Rust",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
    zip_safe=False,
)
