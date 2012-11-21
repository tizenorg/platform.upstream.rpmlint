# -*- coding: utf-8 -*-
#############################################################################
# File          : DistributionCheck.py
# Package       : rpmlint
# Author        : Frederic Lepied
# Created on    : Tue Sep 28 00:05:33 1999
# Version       : $Id: DistributionCheck.py 1732 2010-02-21 11:28:42Z scop $
# Purpose       : check the Distribution specificities in a binary rpm package.
#############################################################################

import re

import rpm

from Filter import addDetails, printWarning
import AbstractCheck
import Config


man_regex = re.compile("/man(?:\d[px]?|n)/")
info_regex = re.compile("(/usr/share|/usr)/info/")
vendor = Config.getOption("Vendor")
distribution = Config.getOption("Distribution")
compress_ext = Config.getOption("CompressExtension", "bz2")

class DistributionCheck(AbstractCheck.AbstractCheck):


    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, "DistributionCheck")

    def check(self, pkg):
        # Check only binary package
        if pkg.isSource():
            return

        if vendor and pkg[rpm.RPMTAG_VENDOR] != vendor:
            printWarning(pkg, "invalid-vendor", pkg[rpm.RPMTAG_VENDOR])

        if distribution and pkg[rpm.RPMTAG_DISTRIBUTION] != distribution:
            printWarning(pkg, "invalid-distribution",
                         pkg[rpm.RPMTAG_DISTRIBUTION])

        if compress_ext:
            for fname in pkg.files():
                if man_regex.search(fname):
                    if not fname.endswith(compress_ext):
                        printWarning(pkg, 'manpage-not-compressed',
                                     compress_ext, fname)
                elif info_regex.search(fname) and \
                        not fname.endswith("/info/dir"):
                    if not fname.endswith(compress_ext):
                        printWarning(pkg, 'infopage-not-compressed',
                                     compress_ext, fname)


# Create an object to enable the auto registration of the test
check = DistributionCheck()

addDetails(
'invalid-vendor',
'''In the "%s" distribution, vendor should be "%s".''' % (distribution, vendor),

'invalid-distribution',
'The distribution value should be "' + distribution + '".',

'manpage-not-compressed',
'''This manual page is not compressed with the %s compression method
(does not have the %s extension). If the compression does not happen
automatically when the package is rebuilt, make sure that you have the
appropriate rpm helper and/or config packages for your target distribution
installed and try rebuilding again; if it still does not happen automatically,
you can compress this file in the %%install section of the spec file.''' \
% (compress_ext, compress_ext),

'infopage-not-compressed',
'''This info page is not compressed with the %s compression method
(does not have the %s extension). If the compression does not happen
automatically when the package is rebuilt, make sure that you have the
appropriate rpm helper and/or config packages for your target distribution
installed and try rebuilding again; if it still does not happen automatically,
you can compress this file in the %%install section of the spec file.''' \
% (compress_ext, compress_ext),
)

# DistributionCheck.py ends here

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
