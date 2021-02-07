# Copyright (c) 2009-2012, Geoffrey Biggs
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Geoffrey Biggs nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# File: pkgconfig.py
# Author: KOLANICH
# Part of pykg-config.

"""Used to extract some required info (such as compiled-in paths) from real pkg-config installed in a system.
"""

__version__ = "$Revision: $"
# $Source$

import os
import re
import subprocess
import sys
from shutil import which

pykg_config_package_name = "pykg_config"

defaultImplsList = ["pkgconf", "pkg-config"]

def discover_pkg_config_impl(path=None, impls=None):
    if impls is None:
        impls = defaultImplsList

    for impl in impls:
        res = which(impl, path=path)
        if res:
            return res
    raise FileNotFoundError("No pkg-config impl is installed in your system")


discovered_pkg_config_command = None

def _get_pkg_config_impl():
    global discovered_pkg_config_command
    if discovered_pkg_config_command is None:
        discovered_pkg_config_command = discover_pkg_config_impl()
    return discovered_pkg_config_command

class Env:
    __slots__ = ("patch", "backup")
    def __init__(self, **kwargs):
        self.patch = kwargs
        self.backup = None
    def __enter__(self):
        self.backup = os.environ.copy()
        os.environ.update(self.patch)
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        os.environ = self.backup

def _call_process(args):
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output = process.communicate()
    output = (
        output[0].strip().decode("utf-8"),
        output[1].strip().decode("utf-8"),
    )
    return_code = process.returncode
    return output[0], output[1], return_code

def call_process(args, **env):
    if env:
        with Env(**env):
            return _call_process(args)
    else:
        return _call_process(args)

def call_pkgconfig(*args, **env):
    return call_process((_get_pkg_config_impl(),) + args, **env)

def call_pykgconfig(*args, **env):
    return call_process(
        (sys.executable, "-m", pykg_config_package_name) + args, **env
    )


# vim: tw=79
