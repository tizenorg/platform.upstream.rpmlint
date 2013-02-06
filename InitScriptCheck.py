# -*- coding: utf-8 -*-
#---------------------------------------------------------------
# Project         : Mandriva Linux
# Module          : rpmlint
# File            : InitScriptCheck.py
# Version         : $Id: InitScriptCheck.py 1893 2011-11-23 20:24:32Z scop $
# Author          : Frederic Lepied
# Created On      : Fri Aug 25 09:26:37 2000
# Purpose         : check init scripts (files in /etc/rc.d/init.d)
#---------------------------------------------------------------

import os
import re

import rpm

from Filter import addDetails, printError, printWarning
import AbstractCheck
import Config
import Pkg
import stat

chkconfig_content_regex = re.compile('^\s*#\s*chkconfig:\s*([-0-9]+)\s+[-0-9]+\s+[-0-9]+')
subsys_regex = re.compile('/var/lock/subsys/([^/"\'\n\s;&|]+)', re.MULTILINE)
chkconfig_regex = re.compile('^[^#]*(chkconfig|add-service|del-service)', re.MULTILINE)
status_regex = re.compile('^[^#]*status', re.MULTILINE)
reload_regex = re.compile('^[^#]*reload', re.MULTILINE)
use_deflevels = Config.getOption('UseDefaultRunlevels', True)
lsb_tags_regex = re.compile('^# ([\w-]+):\s*(.*?)\s*$')
lsb_cont_regex = re.compile('^#(?:\t|  )(.*?)\s*$')
use_subsys = Config.getOption('UseVarLockSubsys', True)

stop_on_removal_regex=re.compile('/etc/init.d/\$service stop > /dev/null')
restart_on_update_regex=re.compile('/etc/init.d/\$service try-restart > /dev/null')
insserv_cleanup_regex=re.compile('^\s*/sbin/insserv /etc/init.d$', re.MULTILINE)

LSB_KEYWORDS = ('Provides', 'Required-Start', 'Required-Stop', 'Should-Start',
                'Should-Stop', 'Default-Start', 'Default-Stop',
                'Short-Description', 'Description')
RECOMMENDED_LSB_KEYWORDS = ('Provides', 'Required-Start', 'Required-Stop',
                            'Default-Stop', 'Short-Description')

class InitScriptCheck(AbstractCheck.AbstractCheck):

    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, 'InitScriptCheck')

    def check(self, pkg):
        # Check only binary package
        if pkg.isSource():
            return

        initscript_list = []


        # check chkconfig call in %post and %preun
        postin = pkg[rpm.RPMTAG_POSTIN] or pkg.scriptprog(pkg[rpm.RPMTAG_POSTINPROG])
        preun = pkg[rpm.RPMTAG_PREUN] or pkg.scriptprog(pkg[rpm.RPMTAG_PREUNPROG])
        postun = pkg[rpm.RPMTAG_POSTUN] or pkg.scriptprog(pkg[rpm.RPMTAG_POSTUNPROG])

        for fname, pkgfile in pkg.files().items():

            if not fname.startswith('/etc/init.d/') and \
                    not fname.startswith('/etc/rc.d/init.d/'):
                continue

            if not stat.S_ISREG(pkgfile.mode):
                continue

            basename = os.path.basename(fname)
            initscript_list.append(basename)
            if pkgfile.mode & 0500 != 0500:
                printError(pkg, 'init-script-non-executable', fname)

            if "." in basename:
                printError(pkg, 'init-script-name-with-dot', fname)

            preun = pkg[rpm.RPMTAG_PREUN] or \
                pkg.scriptprog(rpm.RPMTAG_PREUNPROG)
            if not preun or not stop_on_removal_regex.search(preun):
                printError(pkg, 'init-script-without-%stop_on_removal-preun', fname)

            if not postun or not restart_on_update_regex.search(postun):
                printError(pkg, 'init-script-without-%restart_on_update-postun', fname)

            if not postun or not insserv_cleanup_regex.search(postun):
                printError(pkg, 'init-script-without-%insserv_cleanup-postun', fname)

            status_found = False
            reload_found = False
            chkconfig_content_found = False
            subsys_regex_found = False
            in_lsb_tag = False
            in_lsb_description = False
            lastline = ''
            lsb_tags = {}
            # check common error in file content
            content = None
            try:
                content = Pkg.readlines(pkgfile.path)
            except Exception, e:
                printWarning(pkg, 'read-error', e)
                continue
            content_str = "".join(content)
            for line in content:
                line = line[:-1] # chomp
                # TODO check if there is only one line like this
                if line.startswith('### BEGIN INIT INFO'):
                    in_lsb_tag = True
                    continue
                if line.endswith('### END INIT INFO'):
                    in_lsb_tag = False
                    for kw, vals in lsb_tags.items():
                        if len(vals) != 1:
                            printError(pkg, 'redundant-lsb-keyword', kw)

                    for kw in RECOMMENDED_LSB_KEYWORDS:
                        if kw not in lsb_tags:
                            printWarning(pkg, 'missing-lsb-keyword',
                                         "%s in %s" % (kw, fname))
                if in_lsb_tag:
                    # TODO maybe we do not have to handle this ?
                    if lastline.endswith('\\'):
                        line = lastline + line
                    else:
                        res = lsb_tags_regex.search(line)
                        if not res:
                            cres = lsb_cont_regex.search(line)
                            if not (in_lsb_description and cres):
                                in_lsb_description = False
                                printError(pkg,
                                           'malformed-line-in-lsb-comment-block',
                                           line)
                            else:
                                lsb_tags["Description"][-1] += \
                                    " " + cres.group(1)
                        else:
                            tag = res.group(1)
                            if not tag.startswith('X-') and \
                                    tag not in LSB_KEYWORDS:
                                printError(pkg, 'unknown-lsb-keyword', line)
                            else:
                                in_lsb_description = (tag == 'Description')
                                if tag not in lsb_tags:
                                    lsb_tags[tag] = []
                                lsb_tags[tag].append(res.group(2))
                    lastline = line

                if not status_found and status_regex.search(line):
                    status_found = True

                if not reload_found and reload_regex.search(line):
                    reload_found = True

                res = chkconfig_content_regex.search(line)
                if res:
                    chkconfig_content_found = True
                    if use_deflevels:
                        if res.group(1) == '-':
                            printWarning(pkg, 'no-default-runlevel', fname)
                    elif res.group(1) != '-':
                        printWarning(pkg, 'service-default-enabled', fname)

                res = subsys_regex.search(line)
                if res:
                    subsys_regex_found = True
                    name = res.group(1)
                    if use_subsys and name != basename:
                        error = True
                        if name[0] == '$':
                            value = Pkg.substitute_shell_vars(name, content_str)
                            if value == basename:
                                error = False
                        else:
                            i = name.find('}')
                            if i != -1:
                                name = name[0:i]
                                error = name != basename
                        if error and len(name):
                            if name[0] == '$':
                                printWarning(pkg, 'incoherent-subsys', fname,
                                             name)
                            else:
                                printError(pkg, 'incoherent-subsys', fname,
                                           name)

            if "Default-Start" in lsb_tags:
                if "".join(lsb_tags["Default-Start"]):
                    printWarning(pkg, 'service-default-enabled', fname)

            if not status_found:
                printError(pkg, 'no-status-entry', fname)
            if not reload_found:
                printWarning(pkg, 'no-reload-entry', fname)
            if not chkconfig_content_found:
                printError(pkg, 'no-chkconfig-line', fname)
            if not subsys_regex_found and use_subsys:
                printError(pkg, 'subsys-not-used', fname)
            elif subsys_regex_found and not use_subsys:
                printError(pkg, 'subsys-unsupported', fname)

        if len(initscript_list) == 1:
            pkgname = re.sub("-sysvinit$", "", pkg.name.lower())
            goodnames = (pkgname, pkgname + 'd')
            if initscript_list[0] not in goodnames:
                printWarning(pkg, 'incoherent-init-script-name',
                             initscript_list[0], str(goodnames))


# Create an object to enable the auto registration of the test
check = InitScriptCheck()

addDetails(
'init-script-without-chkconfig-postin',
'''The package contains an init script but doesn't contain a %post with
a call to chkconfig.''',

'postin-without-chkconfig',
'''The package contains an init script but doesn't call chkconfig in its
%post script.''',

'init-script-without-chkconfig-preun',
'''The package contains an init script but doesn't contain a %preun with
a call to chkconfig.''',

'preun-without-chkconfig',
'''The package contains an init script but doesn't call chkconfig in its
%preun script.''',

'missing-lsb-keyword',
'''The package contains an init script that does not contain one of the LSB
init script comment block convention keywords that are recommendable for all
init scripts.  If there is nothing to add to a keyword's value, include the
keyword in the script with an empty value.  Note that as of version 3.2, the
LSB specification does not mandate presence of any keywords.''',

'no-status-entry',
'''In your init script (/etc/rc.d/init.d/your_file), you don't
have a 'status' entry, which is necessary for good functionality.''',

'no-reload-entry',
'''In your init script (/etc/rc.d/init.d/your_file), you don't
have a 'reload' entry, which is necessary for good functionality.''',

'no-chkconfig-line',
'''The init script doesn't contain a chkconfig line to specify the runlevels
at which to start and stop it.''',

'no-default-runlevel',
'''The default runlevel isn't specified in the init script.''',

'service-default-enabled',
'''The service is enabled by default after "chkconfig --add"; for security
reasons, most services should not be. Use "-" as the default runlevel in the
init script's "chkconfig:" line and/or remove the "Default-Start:" LSB keyword
to fix this if appropriate for this service.''',

'subsys-unsupported',
'''The init script uses /var/lock/subsys which is not supported by
this distribution.''',

'subsys-not-used',
'''While your daemon is running, you have to put a lock file in
/var/lock/subsys/. To see an example, look at this directory on your
machine and examine the corresponding init scripts.''',

'incoherent-subsys',
'''The filename of your lock file in /var/lock/subsys/ is incoherent
with your actual init script name. For example, if your script name
is httpd, you have to use 'httpd' as the filename in your subsys directory.
It is also possible that rpmlint gets this wrong, especially if the init
script contains nontrivial shell variables and/or assignments.  These
cases usually manifest themselves when rpmlint reports that the subsys name
starts a with '$'; in these cases a warning instead of an error is reported
and you should check the script manually.''',

'incoherent-init-script-name',
'''The init script name should be the same as the package name in lower case,
or one with 'd' appended if it invokes a process by that name.''',

'init-script-name-with-dot',
'''The init script name should not contain a dot in its name. Some versions
of chkconfig don't work as expected with init script names like that.''',

'init-script-non-executable',
'''The init script should have at least the execution bit set for root
in order for it to run at boot time.''',

'init-script-without-%stop_on_removal-preun',
'''The init script should have a %preun script that calls %stop_on_removal.''',

'init-script-without-%insserv_cleanup-postun',
'''The package doesn't have a %insserv_cleanup call in %postun''',

'init-script-without-%restart_on_update-postun',
''' The package has an init script but is missing the %restart_on_update
call in %postun to automatically restart the daemon. This is optional,
but in most cases it is wanted. Please check.'''
)

# InitScriptCheck.py ends here

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
