Name:		srv
Version:	0
Release:	0
Group:         Development/Tools/Building
Summary:	Bar
License:	GPL
BuildRoot:	%_tmppath/%name-%version-build

%description
%_target
%_target_cpu

%install
install -D -m 755 /bin/sh %buildroot/usr/local/ftp/foo

%clean
rm -rf %buildroot

%files
%defattr(-,root,root)
/usr/local/ftp
