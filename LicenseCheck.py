# -*- coding: utf-8 -*-
# Version         : $Id$

#
# check license files and verify them against declared license in License tag
#

from Filter import addDetails, printError, printWarning
from Pkg import getstatusoutput, is_utf8
import AbstractCheck
import os
import stat
import Config
import rpm
import re

DEFAULT_VALID_LICENSES = ()
VALID_LICENSES = Config.getOption('ValidLicenses', DEFAULT_VALID_LICENSES)
license_regex = re.compile('\(([^)]+)\)|\s(?:and|or)\s')


class LicenseCheck(AbstractCheck.AbstractFilesCheck):
    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(
                self, "LicenseCheck")

    def __checkLicenseFiles(self, pkg):
        for fname, pkgfile in pkg.files().items():
            if not fname.startswith('/usr/share/licenses/'):
                continue

            if not stat.S_ISREG(pkgfile.mode):
                continue

            basename = os.path.basename(fname) 
            st = getstatusoutput(('nomos', pkgfile.path), True)
            print st
            def split_license(license):
                return (x.strip() for x in
                        (l for l in license_regex.split(license) if l))

            if st[0]:
                for line in st[1].splitlines():
                    if 'license(s)' in line:
                        licenses = line.split('license(s) ')[1].split(",")
                        rpm_license = pkg[rpm.RPMTAG_LICENSE]
                        if not rpm_license:
                            continue
                        else:
                            if rpm_license not in VALID_LICENSES:
                                for l1 in split_license(rpm_license):
                                    if l1 in VALID_LICENSES and l1 == licenses[0]:
                                        continue
                                    sp = split_license(l1)
                                    if sp != licenses:
                                        printWarning(pkg, 'licenses-do-not-match', sp, licenses)



    def check(self, pkg):

        if pkg.isSource() or not pkg.licenseFiles():
            return

        self.__checkLicenseFiles(pkg)

check = LicenseCheck()

addDetails(
'licenses-do-not-match',
'''Licenses do not match.''',
'wrong-number-of-licenses',
'''Number of licenses do not match.''',
)

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
