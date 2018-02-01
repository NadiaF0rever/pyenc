# PYENC
encrypt and run your python code

## EXAMPLE

```shell
$ tree .
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
└── c
```

```python
#!/usr/bin/python2.7

import sys
import logging
logging.basicConfig(level=logging.DEBUG, path="a.log", fmt="%(asctime)s %(levelname)s %(msg)s")


import a.b.c.d as A

print dir(A)


from a.b.c import cm

print dir(cm)


if __name__ == "__main__":
    print "hehe wo de ming zi jiao biao di"
    print sys.argv
```

encrypt your python code with **pyenc** `encrypt` sub command

    python pyenc encrypt -R a/ -F c.py -P $PASSWORD

decrypt your python code with **pyenc** `decrypt` sub command

    python pyenc encrypt -R a/ -F c.py -P $PASSWORD

run your python code with **pyenc** `run` sub command

    python pyenc run -P $PASSWORD c.py ni hao a
