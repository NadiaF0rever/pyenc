#!/usr/bin/python2.7
#-*- coding: utf8 -*-

from distutils.core import setup

setup(
        name = "pyenc",
        description = "encrypt and run your python code",
        author = "eeiwant",
        author_email = "eeiwant@gmail.com",
        scripts = ["bin/pyenc"],
        packages = ["pyenc"]
    )
