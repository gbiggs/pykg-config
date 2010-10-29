#!/usr/bin/env python

# Copyright (c) 2009, Geoffrey Biggs
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

# File: test_compatibility.py
# Author: Geoffrey Biggs
# Part of pykg-config.

__version__ = "$Revision: $"
# $Source$

# TODO: Selecting random packages from the list for the tests is a bad idea. It
# doesn't ensure complete repeatability. Instead, the tests should run for each
# package in the list.

import random
import subprocess
import sys
import unittest

class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.packages = [('playercore', '3.1.0-svn'),
                         ('hokuyo_aist', '2.0.0'),
                         ('libxml-2.0', '2.7.7'),
                         ('QtCore', '4.6.3')]
        self.error_package = 'thisisabadpkg'
        self.pykg_config_command = '../pykg-config.py'
        self.pkg_config_command = 'pkg-config'

    def get_random_package(self):
        return random.choice(self.packages)[0]

    def get_random_package_with_version(self):
        return random.choice(self.packages)

    def get_random_package_with_incremented_version(self):
        pkg = self.get_random_package_with_version()
        # Bump the version number of the chosen package
        version = pkg[1].split('.')
        version = [version[0], str(int(version[1]) + 1)] + version[2:]
        return (pkg[0], '.'.join(version))

    def get_random_package_with_decremented_version(self):
        pkg = self.get_random_package_with_version()
        # Drop the version number of the chosen package
        version = pkg[1].split('.')
        if int(version[1]) == 0:
            version = [str(int(version[0]) - 1)] + version[2:]
        else:
            version = [version[0], str(int(version[1]) - 1)] + version[2:]
        return (pkg[0], '.'.join(version))

    def call_process(self, args):
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output = process.communicate()
        output = (output[0].strip(), output[1].strip())
        return_code = process.returncode
        return output[0], output[1], return_code

    def run_test_case(self, args):
        lhs_result = self.call_process([self.pykg_config_command] + args)
        rhs_result = self.call_process([self.pkg_config_command] + args)
        return lhs_result, rhs_result

    def build_error_msg(self, args, lhs, rhs):
        return 'Failed with arguments: {0}\nLHS: {1}\nRHS: {2}'.format(args,
                                                                       lhs,
                                                                       rhs)

    def test_noargs(self):
        lhs, rhs = self.run_test_case([])
        self.assertEqual(lhs, rhs)

    def test_version(self):
        args = ['--version']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs)

    def test_atleast_pkgconfig_greater(self):
        args = ['--atleast-pkgconfig-version=1.0']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs)

    def test_atleast_pkgconfig_equal(self):
        args = ['--atleast-pkgconfig-version=0.23']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs)

    def test_atleast_pkgconfig_less(self):
        args = ['--atleast-pkgconfig-version=0.1']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs)

    def test_modversion_existing_package(self):
        pkg = self.get_random_package_with_version()
        args = ['--modversion', pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[0], pkg[1], self.build_error_msg(args, lhs[0], pkg[1]))

    def test_modversion_nonexisting_package(self):
        pkg = self.get_random_package_with_version()
        args = ['--modversion', pkg[0] + 'blag']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_modversion_no_package(self):
        args = ['--modversion']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_atleast_modversion_greater(self):
        pkg = self.get_random_package_with_incremented_version()
        args = ['--atleast-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_atleast_modversion_equal(self):
        pkg = self.get_random_package_with_version()
        args = ['--atleast-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs[2], '0'))

    def test_atleast_modversion_less(self):
        pkg = self.get_random_package_with_decremented_version()
        args = ['--atleast-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_exact_modversion_greater(self):
        pkg = self.get_random_package_with_incremented_version()
        args = ['--exact-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_exact_modversion_equal(self):
        pkg = self.get_random_package_with_version()
        args = ['--exact-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_exact_modversion_less(self):
        pkg = self.get_random_package_with_decremented_version()
        args = ['--exact-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_max_modversion_greater(self):
        pkg = self.get_random_package_with_incremented_version()
        args = ['--max-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_max_modversion_equal(self):
        pkg = self.get_random_package_with_version()
        args = ['--max-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_max_modversion_less(self):
        pkg = self.get_random_package_with_decremented_version()
        args = ['--max-version', pkg[1], pkg[0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs[2], '1'))

    def test_exists_existing(self):
        pkg = self.get_random_package()
        args = ['--exists', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_exists_nonexisting(self):
        pkg = self.get_random_package()
        args = ['--exists', pkg + 'blag']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_exists_with_correct_version(self):
        pkg = self.get_random_package_with_version()
        args = ['--exists', pkg[0], '=', pkg[1]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_exists_with_incorrect_version(self):
        pkg = self.get_random_package_with_incremented_version()
        args = ['--exists', pkg[0], '=', pkg[1]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 1, self.build_error_msg(args, lhs, rhs))

    def test_get_variable_existing(self):
        args = ['--variable', 'prefix', self.packages[0][0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_get_variable_nonexisting(self):
        args = ['--variable', 'prefix', self.packages[1][0]]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_define_variable(self):
        pkg = self.get_random_package()
        args = ['--define-variable', 'prefix=/usr/local', '--cflags', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))
        self.assertEqual(lhs[2], 0, self.build_error_msg(args, lhs, rhs))

    def test_uninstalled(self):
        pkg = self.get_random_package()
        args = ['--uninstalled', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_list_all(self):
        # The ordering of the list-all output is different between the two
        # programs due to the two different methods used for managing the list
        # of known packages and their order of precedence.
        args = ['--list-all']
        lhs, rhs = self.run_test_case(args)
        lhs_pkgs = lhs[0].split('\n')
        rhs_pkgs = rhs[0].split('\n')
        for lhs_pkg in lhs_pkgs:
            self.assert_(lhs_pkg in rhs_pkgs, '"{0}" not in RHS'.format(lhs_pkg))
        for rhs_pkg in rhs_pkgs:
            self.assert_(rhs_pkg in lhs_pkgs, '"{0}" not in LHS'.format(rhs_pkg))
        self.assertEqual(len(lhs_pkgs), len(rhs_pkgs))
        self.assertEqual(lhs[1], rhs[1], self.build_error_msg(args, lhs[1], rhs[1]))
        self.assertEqual(lhs[2], rhs[2], self.build_error_msg(args, lhs[2], rhs[2]))

    def test_print_errors_with_error(self):
        # This test relies on there being an error present. I have a dead
        # symlink in one of the searched dirs to cause an error (no such file
        # or dir) when performing the list-all command.
        args = ['--cflags', '--print-errors', self.error_package]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_print_errors_without_error(self):
        # This test relies on using a command that does _not_ produce any
        # errors.
        pkg = self.get_random_package()
        args = ['--print-errors', '--modversion', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_silence_errors_with_error(self):
        # This test relies on there being an error present. I have a dead
        # symlink in one of the searched dirs to cause an error (no such file
        # or dir) when performing the list-all command.
        args = ['--cflags', '--silence-errors', self.error_package]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_silence_errors_without_error(self):
        # This test relies on using a command that does _not_ produce any
        # errors.
        pkg = self.get_random_package()
        args = ['--silence-errors', '--modversion', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_errors_to_stdout(self):
        args = ['--cflags', '--errors-to-stdout', self.error_package]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_short_errors(self):
        args = ['--cflags', '--short-errors', 'nonexistentpackage']
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_libs(self):
        pkg = self.get_random_package()
        args = ['--libs', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_static(self):
        pkg = self.get_random_package()
        args = ['--libs', '--static', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_libs_only_l(self):
        pkg = self.get_random_package()
        args = ['--libs-only-l', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_libs_only_other(self):
        pkg = self.get_random_package()
        args = ['--libs-only-other', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_libs_only_big_l(self):
        pkg = self.get_random_package()
        args = ['--libs-only-L', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_cflags(self):
        pkg = self.get_random_package()
        args = ['--cflags', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_cflags_only_big_i(self):
        pkg = self.get_random_package()
        args = ['--cflags-only-I', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))

    def test_cflags_only_other(self):
        pkg = self.get_random_package()
        args = ['--cflags-only-other', pkg]
        lhs, rhs = self.run_test_case(args)
        self.assertEqual(lhs, rhs, self.build_error_msg(args, lhs, rhs))


if __name__ == '__main__':
    unittest.main()

