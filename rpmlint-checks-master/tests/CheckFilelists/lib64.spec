Name:		lib64
Version:	0
Release:	0
Group:         Development/Tools/Building
Summary:	Bar
License:	GPL
BuildRoot:	%_tmppath/%name-%version-build
BuildArch:      noarch

%description
%_target
%_target_cpu

%install
install -D -m 755 /lib/ld-linux.so.2 %buildroot/lib64/ld-linux.so.2

%clean
rm -rf %buildroot

%files
%defattr(-,root,root)
/lib64/ld-linux.so.2
