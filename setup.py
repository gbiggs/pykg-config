#!/usr/bin/env python

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

__version__ = "$Revision: $"
# $Source$

from distutils.core import setup
from distutils.command.build_py import build_py
from distutils import log
import os.path
import sys

scripts = ['pykg-config.py']
if sys.platform == 'win32':
    scripts.append('pkg-config.bat')


class BuildWithConfigure(build_py):
    user_options = build_py.user_options + [
        ('with-pc-path=', None, 'default search path for .pc files'),
        ]

    def __init__(self, dist):
        build_py.__init__(self, dist)
        self.with_pc_path = None

    def finalize_options(self):
        build_py.finalize_options(self)
        self.ensure_dirname('with_pc_path')

    def run(self):
        build_py.run(self)
        config_dest = os.path.join(self.build_lib, 'pykg_config', 'install_config.py')
        log.info("creating configuration file at %s", config_dest)
        with open(config_dest, 'w') as f:
            if self.with_pc_path:
                f.write('pc_path = "' + self.with_pc_path + '"\n')
            else:
                f.write('pc_path = None\n')
        # TODO: should byte-compile the config file here (see
        # build_py.byte_compile())


setup(name='pykg-config',
      version='1.2.0',
      description='pkg-config replacement.',
      author='Geoffrey Biggs',
      author_email='git@killbots.net',
      url='http://github.com/gbiggs/pykg-config',
      license='BSD',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development',
          'Topic :: Utilities'
          ],
      packages=['pykg_config'],
      scripts=scripts,
      cmdclass={'build_py':BuildWithConfigure}
      )
