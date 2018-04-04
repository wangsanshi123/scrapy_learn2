#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import strftime, localtime


class ErrorUtil:
    def record(self, e):
        msg = str(e)
        now = strftime("%Y-%m-%d-%H", localtime())
        file = now + ".txt"
        with open(file, "a") as f:
            f.write(msg + "\n")

        pass

    pass


if __name__ == '__main__':
    for i in range(10):
        ErrorUtil().record("ytx\n")
