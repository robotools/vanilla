#!/usr/bin/env python

import sys
from setuptools import setup

if "sdist" in sys.argv:
    import os
    import subprocess
    import shutil
    docFolder = os.path.join(os.getcwd(), "documentation")
    # remove existing
    doctrees = os.path.join(docFolder, "build", "doctrees")
    if os.path.exists(doctrees):
        shutil.rmtree(doctrees)
    # compile
    p = subprocess.Popen(["make", "html"], cwd=docFolder)
    p.wait()
    # remove doctrees
    shutil.rmtree(doctrees)



setup(name="vanilla",
    version="0.1",
    description="A Pythonic wrapper around Cocoa.",
    author="Tal Leming",
    author_email="tal@typesupply.com",
    url="https://github.com/robotools/vanilla",
    license="MIT",
    packages=["vanilla", "vanilla.test"],
    package_dir={"":"Lib"}
)
