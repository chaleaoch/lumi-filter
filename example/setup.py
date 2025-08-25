# -*- coding: utf-8 -*-

import os
import shutil

from Cython.Build import cythonize
from setuptools import Extension, setup

ext_modules = []
curr_path = os.path.dirname(__file__)
src = os.path.join(curr_path, "src")
build = os.path.join(curr_path, "build")


def path_to_module(path):
    path = path.replace(src, "")
    ret = os.path.splitext(path[1:])[0].replace("/", ".")
    return ret


removed_file_path_list = []
for path, dirs, files in os.walk(src):
    for filename in files:
        file_path = os.path.join(path, filename)
        if "__init__" != os.path.splitext(filename)[0] and ".py" == os.path.splitext(filename)[1]:
            print(file_path)
            ext_modules.append(Extension(path_to_module(file_path), [file_path]))
            removed_file_path_list.append(file_path)


setup(
    author="chaleaoch<chaleaoch@gmail.com>",
    author_email="chaleaoch@gmail.com",
    url="-",
    package_data={},
    include_package_data=True,
    install_requires=[],
    zip_safe=False,
    classifiers=[],
    ext_modules=cythonize(ext_modules, compiler_directives={"always_allow_keywords": True}),
    package_dir={"": src},
)

for file_path in removed_file_path_list:
    os.remove(file_path)
    os.remove(file_path.replace(".py", ".c"))
shutil.rmtree(build)
