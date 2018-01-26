#!/usr/bin/python2.7
#-*- coding: utf8 -*-


try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import hashlib

from Crypto.Cipher import AES


from . import PyEncError


get_cipher = None

class PyEncIOError(PyEncError):
    pass


CIPHER_FILE_READ = 1
CIPHER_FILE_WRITE = 2

class CipherFile(object):
    '''
    file-like object对象，用于对加密文件和非加密文件的操作有一致的接口

    只支持 读，写 两种模式不支持 读写 模式
    '''

    MAGIC = "CFBIAODI"


    def __init__(self, path, mode):

        if not get_cipher:
            raise PyEncError("cipher file not initialized call init first")

        self.__cipher = get_cipher()
        self.__io = None
        self.__fp = None

        if mode == CIPHER_FILE_READ:
            enc = False
            with open(path, "rb") as fp:
                magic = fp.read(8)
                if magic == self.MAGIC:
                    enc = True

            #if not ignore and not enc:
            #    raise PyEncIOError("invalid cipher file %s" % path)

            self._create_read_file(path, enc)


        elif mode == CIPHER_FILE_WRITE:
            self.__io = StringIO.StringIO()
            self.__fp = open(path, "wb")
            self.__fp.write(self.MAGIC)

            self.write = self.__cipher_encrypt_write
            self.close = self.__cipher_encrypt_done

            self.read = self.__not_support
            self.readline = self.__not_support
            self.readlines = self.__not_support

        else:
            raise ValueError("invalid open mode %s" % mode)



    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return exc_type and True or False


    def __pass(self, *arg, **kv):
        pass

    def close(self):
        if self.__io:
            self.__io.close()

        if self.__fp:
            self.__fp.close()

    def __not_support(self, *arg, **kv):
        raise NotImplementedError

    def __cipher_encrypt_done(self):
        data = self.__io.getvalue()
        pad = 16 - len(data) % 16

        #增加填充数据 https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS7
        padding = "".join([chr(pad) for i in xrange(0, pad)])

        self.__fp.write(self.__cipher.encrypt(data + padding))
        self.__io.close()
        self.__fp.close()


    def __cipher_encrypt_write(self, s):
        self.__io.write(s)


    def _create_read_file(self, path, enc):

        if enc:
            self.__io = StringIO.StringIO()
            with open(path, "rb") as fp:
                fp.seek(0, 2)
                size = fp.tell()
                fp.seek(len(self.MAGIC), 0)

                data = fp.read(size - len(self.MAGIC))
                data = self.__cipher.decrypt(data)

                #移除掉填充数据 https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS7
                pad = ord(data[-1])
                data = data[:-pad]

                self.__io.write(data)
                self.__io.seek(0, 0)

                self.write = self.__not_support

                self.read = self.__io.read
                self.readline = self.__io.readline
                self.readlines = self.__io.readlines

        else:
            fp = open(path, "rU")
            self.__fp = fp

            self.read = fp.read
            self.readline = fp.readline
            self.readlines = fp.readlines

            self.write = self.__not_support
            


def Init(password):
    global get_cipher
    #初始化key, iv
    key, iv = evp_bytestokey(hashlib.sha1, password, "emanon..", 5, 32, 16)

    def _cipher():
        return AES.new(key, mode=AES.MODE_CBC, IV=iv)
    get_cipher = _cipher


def Open(path, mode):
    return CipherFile(path, mode)


def evp_bytestokey(md, password, salt, count, key_length, iv_length):
    md_buf = ""
    key = ""
    iv = ""

    addmd = 0

    while key_length > len(key) or iv_length > len(iv):
        c = md()
        if addmd:
            c.update(md_buf)
        addmd += 1
        c.update(password)
        c.update(salt)
        md_buf = c.digest()
        for i in range(1, count):
            c = md()
            c.update(md_buf)
            md_buf = c.digest()

        md_buf2 = md_buf

        if key_length > len(key):
            key, md_buf2 = key + md_buf2[:key_length - len(key)], md_buf2[key_length - len(key):]

        if iv_length > len(iv):
            iv, md_buf2 = iv + md_buf2[:iv_length - len(iv)], md_buf2[iv_length - len(iv):]

    return key, iv
