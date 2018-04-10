#!/usr/bin/python2.7
#-*- coding: utf8 -*-

'''
Copyright NadiaF0rever
'''

from distutils.core import setup
from Cython.Build import cythonize

setup(
        name = "pyenc",
        description = "encrypt and run your python code",
        author = "eeiwant",
        author_email = "eeiwant@gmail.com",
        scripts = ["bin/pyenc"],
        ext_modules = cythonize("pyenc/*.pyx"),
        packages = ["pyenc"]
    )
