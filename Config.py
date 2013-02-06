# -*- coding: utf-8 -*-
#############################################################################
# File          : Config.py
# Package       : rpmlint
# Author        : Frederic Lepied
# Created on    : Fri Oct 15 20:04:25 1999
# Version       : $Id: Config.py 1871 2011-06-18 09:40:52Z scop $
# Purpose       : handle configuration options. To be used from config files.
#############################################################################

import locale
import os.path
import re

try:
    from __version__ import __version__
except ImportError:
    __version__ = 'devel'

DEFAULT_CHECKS = (
                  "TagsCheck",
                  "BinariesCheck",
                  "ConfigCheck",
                  "FilesCheck",
                  "DocFilesCheck",
                  "FHSCheck",
                  "I18NCheck",
                  "MenuCheck",
                  "PostCheck",
                  "InitScriptCheck",
                  "SourceCheck",
                  "SpecCheck",
                  "NamingPolicyCheck",
                  "ZipCheck",
                  "PamCheck",
                  "RpmFileCheck",
                  "MenuXDGCheck",
                  )

USEUTF8_DEFAULT = False
try:
    if locale.getpreferredencoding() == 'UTF-8':
        USEUTF8_DEFAULT = True
except:
    try:
        if re.match('utf', locale.getdefaultlocale()[1], re.I):
            USEUTF8_DEFAULT = True
    except:
        pass

info = False
no_exception = False

# handle the list of checks to load
_checks = []
_checks.extend(DEFAULT_CHECKS)

def addCheck(check):
    check = re.sub('\.py[co]?$', '', check)
    if check not in _checks:
        _checks.append(check)

def allChecks():
    if _checks == []:
        defaultChecks()
    return _checks

def defaultChecks():
    resetChecks()
    _checks.extend(DEFAULT_CHECKS)

def resetChecks():
    global _checks

    _checks = []

# handle the list of directories to look for checks

_dirs = ["/usr/share/rpmlint"]

def addCheckDir(dir):
    d = os.path.expanduser(dir)
    if d not in _dirs:
        _dirs.insert(0, d)

def checkDirs():
    return _dirs

# handle options

_options = {}

def setOption(name, value):
    _options[name] = value

def getOption(name, default = ""):
    try:
        return _options[name]
    except:
        return default

# List of filters
_filters = []
_filters_re = None

_filters_non_except = []
_filters_non_except_re = None

_filters_except = []
_filters_except_re = None

def addFilter(s):
    global _filters_re
    global _filters_except

    if len(_filters_except):
        _filters.append(s)
        _filters_re = None
    else:
        _filters_non_except.append(s)
        _filters_non_except_re = None


def removeFilter(s):
    global _filters_re

    try:
        _filters.remove(s)
    except:
        pass
    else:
        _filters_re = None

_scoring = {}

def setBadness(s, score):
    global _scoring
    _scoring[s] = score

def setFilterException(s):
    global _filters_except

    _filters_except.append(s)

def badness(s):
    return _scoring.get(s, 0)

_non_named_group_re = re.compile('[^\\](\()[^:]')
def isFiltered(s):
    global _filters_re
    global _filters_except
    global _filters_except_re
    global _filters_non_except
    global _filters_non_except_re

    if _filters_non_except_re == None and len(_filters_non_except):
        _filters_non_except_re = '(?:' + _filters_non_except[0] + ')'

        for idx in range(1, len(_filters_non_except)):
            # to prevent named group overflow that happen when there is too
            # many () in a single regexp: AssertionError: sorry, but this
            # version only supports 100 named groups
            if '(' in _filters_non_except[idx]:
                _non_named_group_re.subn('(:?', _filters_non_except[idx])
            _filters_non_except_re = _filters_non_except_re + '|(?:' + _filters_non_except[idx] +')'
        _filters_non_except_re = re.compile(_filters_non_except_re)

    if _filters_re == None and len(_filters):
        _filters_re = '(?:' + _filters[0] + ')'

        for idx in range(1, len(_filters)):
            # to prevent named group overflow that happen when there is too
            # many () in a single regexp: AssertionError: sorry, but this
            # version only supports 100 named groups
            if '(' in _filters[idx]:
                _non_named_group_re.subn('(:?', _filters[idx])
            _filters_re = _filters_re + '|(?:' + _filters[idx] +')'
        _filters_re = re.compile(_filters_re)

    if _filters_except_re == None and len(_filters_except):
        _filters_except_re = '(?:' + _filters_except[0] + ')'

        for idx in range(1, len(_filters_except)):
            # to prevent named group overflow that happen when there is too
            # many () in a single regexp: AssertionError: sorry, but this
            # version only supports 100 named groups
            if '(' in _filters_except[idx]:
                _non_named_group_re.subn('(:?', _filters_except[idx])
            _filters_except_re = _filters_except_re + '|(?:' + _filters_except[idx] +')'
        _filters_except_re = re.compile(_filters_except_re)

    if not no_exception:

        if _filters_non_except_re and _filters_non_except_re.search(s):
            return True
        if _filters_except_re and _filters_except_re.search(s):
            return False
        if _filters_re and _filters_re.search(s):
            return True

    return False

# Config.py ends here

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
