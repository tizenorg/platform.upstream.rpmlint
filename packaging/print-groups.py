
import Config
execfile("rpmgroups.config")


VALID_GROUPS = Config.getOption('ValidGroups', None)
VALID_DOMAINS = Config.getOption('ValidDomains', None)
VALID_SUBDOMAINS = Config.getOption('ValidSubDomains', None)
VALID_NONE_DOMAINS = Config.getOption('ValidNoneDomains', None)

if VALID_GROUPS is None: # get defaults from rpm package only if it's not set
    VALID_GROUPS = Pkg.get_default_valid_rpmgroups()
valid_groups = VALID_GROUPS
app_groups = ()
for d in VALID_DOMAINS:
    if d == 'Applications':
        for dd in ['Multimedia', 'Social', 'Web', 'Telephony', 'Messaging', 'PIM', 'Network', 'Navigation', 'Other', 'Game', 'Tasks', 'Music', 'Photo', 'Video']:
            app_groups = app_groups + ("%s/%s" %(d,dd), )
        continue
    for sd in VALID_SUBDOMAINS:
        valid_groups = valid_groups + ("%s/%s" %(d,sd), )

valid_groups = valid_groups + app_groups
valid_groups = valid_groups + VALID_NONE_DOMAINS
for g in sorted(valid_groups):
    print g
