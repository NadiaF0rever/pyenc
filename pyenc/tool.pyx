#!/usr/bin/python2.7
#-*- coding: utf8 -*-

'''
Copyright NadiaF0rever
'''

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import os
import re
import sys
import argparse

import setproctitle

from . import hook

_MODE_ENC = "encrypt"
_MODE_DEC = "decrypt"
_MODE_RUN = "run"

def obsucre_password():
    pass

def pyenc_tool():
    from . import cipher_file

    #avoid _build_pyenc_cb appear in global namespace
    def _build_pyenc_cb(cb):

        def _pyenc_process_files_cb(dirs, files, password, strict):
            process_files = set()
            [process_files.add(i) for i in files]

            def walk_cb(args, base_dir, files):
                for f in files:
                    if f.endswith(".py"):
                        process_files.add(os.path.join(base_dir, f))


            cipher_file.Init(strict)
            opener = cipher_file.BuildOpener(password)

            for dir_ in dirs:
                os.path.walk(dir_, walk_cb, None)

            for f in process_files:
                cb(f, opener)

        return _pyenc_process_files_cb


    def _pyenc_enc_cb(path, _opener):
        io = StringIO.StringIO()
        with open(path, "r") as fp:
            io.write(fp.read())
        io.seek(0, 0)

        with _opener(path, cipher_file.CIPHER_FILE_WRITE) as fp:
            fp.write(io.read())

        io.close()

    def _pyenc_dec_cb(path, _opener):
        io = StringIO.StringIO()
        with _opener(path, cipher_file.CIPHER_FILE_READ) as fp:
            io.write(fp.read())
        io.seek(0, 0)

        with open(path, "w") as fp:
            fp.write(io.read())

        io.close()

    pyenc_enc_files = _build_pyenc_cb(_pyenc_enc_cb)
    pyenc_dec_files = _build_pyenc_cb(_pyenc_dec_cb)


    PROG="pyenc"
    DEF_PASSWD = "emanon"
    RUN_CMD_ONLY = True

    parser = argparse.ArgumentParser(prog=PROG,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    sub_parser = parser.add_subparsers(help="run pyenc in different mode")

    common_argument = (
            (("-P", ), {"type": str, "dest": "password", "default": "",
                "help": "specific encrypt/decrypt password"}),

            (("--strict", ), {"action": "store_true", "dest": "strict",
                "help": "whether pyenc will throw exception if some python files are not encrypt"}),

            (("-R", ), {"dest": "dirs", "default": [], "action": "append",
                "help": "specific encrypt/decrypt directory "
                " all .py file in direcrtory will be processed"}),

            (("-F", ), {"dest": "files", "default": [], "action": "append",
                "help": "specific encrypt/decrypt .py file"})
    )


    if not RUN_CMD_ONLY:
        parser_enc = sub_parser.add_parser("encrypt",
                help="encrypt specific python files")
        parser_enc.set_defaults(mode=_MODE_ENC)

        parser_dec = sub_parser.add_parser("decrypt",
                help="decrypt specific python files which encrypted by pyenc")
        parser_dec.set_defaults(mode=_MODE_DEC)

        for args, kvargs in common_argument:
            parser_enc.add_argument(*args, **kvargs)
            parser_dec.add_argument(*args, **kvargs)


    parser_run = sub_parser.add_parser("run", help="run python programme which encrypted by pyenc")
    parser_run.set_defaults(mode=_MODE_RUN)

    pwd_arg, pwd_kvarg = common_argument[0]
    parser_run.add_argument(*pwd_arg, **pwd_kvarg)

    strict_arg, strict_kvarg = common_argument[1]
    parser_run.add_argument(*strict_arg, **strict_kvarg)

    parser_run.add_argument("--prefix", dest="prefixes", action="append", default=[],
            help="all python module which path begin with prefix will be hooked by pyenc"
            " default is basepath(main)")

    parser_run.add_argument("main", type=str, help="specific the main python programme file")
    parser_run.add_argument("args", nargs=argparse.REMAINDER)

    op = parser.parse_args()

    if not op.password:
        op.password = DEF_PASSWD


    if op.mode == _MODE_ENC:
        return pyenc_enc_files(op.dirs, op.files, op.password, op.strict)

    elif op.mode == _MODE_DEC:
        return pyenc_dec_files(op.dirs, op.files, op.password, op.strict)


    cipher_file.Init(op.strict)
    cipher_opener = cipher_file.BuildOpener(op.password)

    if not op.prefixes:
        op.prefixes.append(os.path.dirname(op.main))

    hook.HookObj.Init(op.prefixes)

    #add path hook
    sys.path_hooks.append(hook.Hook)
    #reset import cache
    sys.path_importer_cache = {}

    #set env for run op.main
    sys.argv = op.args
    sys.argv.insert(0, op.main)

    sys.path.append(os.path.dirname(op.main))

    with cipher_file.Open(op.main, cipher_file.CIPHER_FILE_READ) as fp:
        code = compile(fp.read(), op.main, "exec")

    global_dict = globals()
    global_dict["__name__"] = "__main__"
    exec code in global_dict
