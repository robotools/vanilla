#!/usr/bin/env python

# import sys
from setuptools import setup


# if "sdist" in sys.argv:
#     import os
#     import subprocess
#     import shutil
#     docFolder = os.path.join(os.getcwd(), "Documentation")
#     # remove existing
#     doctrees = os.path.join(docFolder, "build", "doctrees")
#     if os.path.exists(doctrees):
#         shutil.rmtree(doctrees)
#     # compile
#     p = subprocess.Popen(["make", "html"], cwd=docFolder)
#     p.wait()
#     # remove doctrees
#     shutil.rmtree(doctrees)


with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="cocoa-vanilla",
    use_scm_version={"write_to": "Lib/vanilla/_version.py"},
    description="A Pythonic wrapper around Cocoa.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tal Leming",
    author_email="tal@typesupply.com",
    maintainer="Just van Rossum, Frederik Berlaen",
    maintainer_email="justvanrossum@gmail.com",
    install_requires=["pyobjc"],
    setup_requires=["setuptools_scm"],
    url="https://github.com/robotools/vanilla",
    license="MIT",
    packages=["vanilla", "vanilla.test"],
    package_dir={"": "Lib"},
    platforms=["macOS"],
    python_requires=">=3.6",
)
