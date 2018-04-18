#!/usr/bin/python2.7
#-*- coding: utf8 -*-

'''
Copyright NadiaF0rever
'''

from distutils.core import setup
from Cython.Build import cythonize

import re
import os

if __name__ == "__main__":
    PATH = "pyenc/tool.pyx"

    def replace(pattern, repl):
        with open(PATH) as fp:
            data = fp.read()

        data = re.sub(pattern, repl, data)

        with open(PATH, "w") as fp:
            fp.write(data)

    if os.getenv("PYENC_DEF_PASS"):
        replace(r'DEF_PASSWD\s*=\s*"([^"]+)"', 'DEF_PASSWD = "%s"' % os.getenv("PYENC_DEF_PASS"))

    if os.getenv("PYENC_RUN_ONLY"):
        replace(r'RUN_CMD_ONLY\s*=\s*False', 'RUN_CMD_ONLY = True')

    setup(
            name = "pyenc",
            description = "encrypt and run your python code",
            author = "eeiwant",
            author_email = "eeiwant@gmail.com",
            scripts = ["bin/pyenc"],
            ext_modules = cythonize("pyenc/*.pyx"),
            packages = ["pyenc"],

            keywords = [
                "Requires: cython",
                "Requires: pycrypto",
                "Requires: setproctitle",
            ]
    )
