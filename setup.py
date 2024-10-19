import re
from pathlib import Path

from setuptools import setup
from setuptools_rust import Binding, RustExtension

version = re.search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    Path("neofoodclub/__init__.py").read_text(),
    re.MULTILINE,
)

if not version:
    raise RuntimeError("version is not set")
else:
    version = version[1]

packages = [
    "neofoodclub",
]

package_data = {
    "neofoodclub": ["py.typed", "neofoodclub.pyi"],
}

setup(
    name="neofoodclub.py",
    author="diceroll123",
    description="A Python implementation of functionality used in https://neofood.club",
    license="MIT",
    license_file="LICENSE",
    url="https://github.com/diceroll123/neofoodclub.py",
    version=version,
    packages=packages,
    package_data=package_data,
    rust_extensions=[RustExtension("neofoodclub.neofoodclub", binding=Binding.PyO3)],
    python_requires=">=3.9.0",
    classifiers=[
        "Programming Language :: Rust",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Typing :: Typed",
    ],
    zip_safe=False,
    include_package_data=True,
)
