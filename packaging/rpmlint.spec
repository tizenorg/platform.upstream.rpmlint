Name:           rpmlint
BuildRequires:  python-rpm
BuildRequires:  xz
Summary:        Rpm correctness checker
License:        GPL-2.0+
Group:          System/Packages
Version:        1.4
Release:        0
Source0:        http://rpmlint.zarb.org/download/rpmlint-%{version}.tar.bz2
Source1:        rpmlint-checks-master.tar.gz
Source2:        config
Source10:       rpmgroups.config
Source11:       pie.config
Source100:      syntax-validator.py
Url:            http://rpmlint.zarb.org/
Requires:       /usr/bin/readelf
Requires:       bash
Requires:       cpio
Requires:       dash
Requires:       desktop-file-utils
Requires:       file
Requires:       findutils
Requires:       python-magic
Requires:       python-rpm
BuildArch:      noarch
%py_requires

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%setup -q -n rpmlint-%{version}  -a1
cp %{S:2} .
%build
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
# the provided bash-completion does not work and only prints bash errors
rm -rf  $RPM_BUILD_ROOT/etc/bash_completion.d
mv $RPM_BUILD_ROOT/etc/rpmlint/config $RPM_BUILD_ROOT/usr/share/rpmlint/config
head -n 8 $RPM_BUILD_ROOT/usr/share/rpmlint/config > $RPM_BUILD_ROOT/etc/rpmlint/config
# make sure that the package is sane
python -tt %{SOURCE100} $RPM_BUILD_ROOT/usr/share/rpmlint/*.py $RPM_BUILD_ROOT/usr/share/rpmlint/config
%__install -m 644 %{SOURCE10} %{buildroot}/%{_sysconfdir}/rpmlint/
%__install -m 644 %{SOURCE11} %{buildroot}/%{_sysconfdir}/rpmlint/


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
%license COPYING 
%{_prefix}/bin/*
%{_prefix}/share/rpmlint
%config(noreplace) /etc/rpmlint/config
%config %{_sysconfdir}/rpmlint/rpmgroups.config
%config %{_sysconfdir}/rpmlint/pie.config
%dir /etc/rpmlint
%doc /usr/share/man/man1/rpmlint.1.gz

