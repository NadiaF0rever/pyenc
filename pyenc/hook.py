#!/usr/bin/python2.7
#-*- coding: utf8 -*-

import os
import imp
import sys
import logging

from . import cipher_file

class HookObj(object):

    FILE_IS_EXTENSION = staticmethod(lambda info_: info_[2] == imp.C_EXTENSION)

    PREFIXES = None

    @classmethod
    def Init(cls, prefixes=[]):
        cls.PREFIXES = [os.path.abspath(i) for i in prefixes]


    def __init__(self, path):
        if not os.path.exists(path):
            raise ImportError

        if self.PREFIXES:
            for p in self.PREFIXES:
                if path.startswith(p):
                    break

            else:
                raise ImportError

        self._base_path = path
        logging.debug("set_base_path: %s %s", self._base_path, self)


    def get_filename(self, fullname):
        path, _ = self._get_fileinfo(fullname)
        return path

    def get_code(self, fullname):
        path, info = self._get_fileinfo(fullname)
        if HookObj.FILE_IS_EXTENSION(info):
            return None

        with cipher_file.Open(path, cipher_file.CIPHER_FILE_READ) as fp:
            data = fp.read()
            code = compile(data, "<string>", "exec")
            return code


    def is_package(self, fullname):
        path = self.get_filename(fullname)
        return path.endswith("__init__.py")


    def find_module(self, fullname, path=None):
        logging.debug("find_module fullname: %s path: %s", fullname, path)

        path = self.get_filename(fullname)
        if path:
            return self

        return None


    def load_module(self, fullname):
        logging.debug("load_module fullname: %s", fullname)

        path, info = self._get_fileinfo(fullname)
        if HookObj.FILE_IS_EXTENSION(info):
            with open(path, info[1]) as fp:
                return imp.load_module(fullname, fp, path, info)


        code = self.get_code(fullname)
        ispkg = self.is_package(fullname)

        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__loader__ = self
        module.__file__ = self.get_filename(fullname)

        if ispkg:
            module.__path__ = [os.path.dirname(path)]
            module.__package__ = fullname

        else:
            module.__package__ = fullname.rpartition(".")[0]

        sys.modules[fullname] = module

        exec code in module.__dict__

        logging.debug("LOAD %s %s", fullname, dir(module))

        return module


    def _get_fileinfo(self, fullname):
        if fullname.find(".") != -1:
            fields = fullname.split(".")
            basename = os.path.join(*fields[:-1])
            modname = fields[-1]

            assert(self._base_path.endswith(basename))

        else:
            modname = fullname


        prefix = self._base_path
        logging.debug("prefix: %s modname: %s", prefix, modname)

        pkg_path = os.path.join(prefix, os.path.join(modname, "__init__.py"))
        if os.path.isfile(pkg_path):
            return pkg_path, (".py", "U", imp.PY_SOURCE)

        for suffix, mode, type_ in imp.get_suffixes():
            if suffix == imp.PY_COMPILED:
                continue

            file_name = modname + suffix
            file_path = os.path.join(prefix, file_name)
            if os.path.isfile(file_path):
                return file_path, (suffix, mode, type_)

        return None, None




def Hook(path):
    return HookObj(path)

if __name__ == "__main__":
    sys.path_hooks.append(Hook)
    sys.path_importer_cache = {}

    from collections import namedtuple
