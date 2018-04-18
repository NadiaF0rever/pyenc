# PYENC
encrypt and run your python code

## REQUIRE
`python2.7`, `cython`, `pycrypto`, `setproctitle`

## INSTALL
```shell
python setup.py install
```

### ENV
#### PYENC_DEF_PASS
change pyenc default password 

    env PYENC_DEF_PASS=your_default_pass python setup.py install

#### PYENC_RUN_ONLY
disable pyenc `encrypt`, `decrypt` sub command

    env PYENC_RUN_ONLY=1 python setup.py install


## EXAMPLE

```shell
.
├── a
│   ├── am.py
│   ├── b
│   │   ├── bm.py
│   │   ├── c
│   │   │   ├── cm.py
│   │   │   ├── d
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
├── cmodule
│   ├── cm.so
│   └── pm.py
├── c.py
└── d.py
```
encrypt your python code with **pyenc** `encrypt` sub command

    pyenc encrypt -R a/ -R cmodule -F c.py -F d.py -P $PASSWORD

decrypt your python code with **pyenc** `decrypt` sub command

    pyenc decrypt -R a/ -R cmodule -F c.py -F d.py -P $PASSWORD

run your python code with **pyenc** `run` sub command

    pyenc run -P $PASSWORD c.py arg1 arg2 arg3 argn

run `pyenc -h` for help
