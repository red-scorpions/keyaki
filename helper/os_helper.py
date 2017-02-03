# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

def change_ps(path):
    ps = os.sep
    path = path.replace('/',ps)
    return path