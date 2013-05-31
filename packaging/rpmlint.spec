Name:           rpmlint
Version:        1.4
Release:        0
License:        GPL-2.0+
Summary:        Rpm correctness checker
Url:            http://rpmlint.zarb.org/
Group:          Development/Packaging
Source0:        http://rpmlint.zarb.org/download/rpmlint-%{version}.tar.bz2
Source1:        rpmlint-checks-master.tar.gz
Source2:        config
Source10:       rpmgroups.config
Source11:       pie.config
Source12:       licenses.config
Source100:      syntax-validator.py
Source1001:     rpmlint.manifest
BuildRequires:  python-rpm
BuildRequires:  xz
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

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%setup -q -n rpmlint-%{version}  -a1
cp %{SOURCE1001} .
cp %{SOURCE2} .
# Only move top-level python files
chmod 0755 rpmlint-checks-master/*.py
mv rpmlint-checks-master/*.py .

%build
make %{?_smp_mflags}

%install
%make_install
# the provided bash-completion does not work and only prints bash errors
rm -rf  %{buildroot}%{_sysconfdir}/bash_completion.d
mv %{buildroot}%{_sysconfdir}/rpmlint/config %{buildroot}%{_datadir}/rpmlint/config
head -n 8 %{buildroot}%{_datadir}/rpmlint/config > %{buildroot}%{_sysconfdir}/rpmlint/config
# make sure that the package is sane
python -tt %{SOURCE100} %{buildroot}%{_datadir}/rpmlint/*.py %{buildroot}%{_datadir}/rpmlint/config
install -m 644 %{SOURCE10} %{buildroot}/%{_sysconfdir}/rpmlint/
install -m 644 %{SOURCE11} %{buildroot}/%{_sysconfdir}/rpmlint/
install -m 644 %{SOURCE12} %{buildroot}/%{_sysconfdir}/rpmlint/


%files
%manifest %{name}.manifest
%defattr(-,root,root,0755)
%license COPYING
%{_bindir}/*
%{_datadir}/rpmlint
%config(noreplace) %{_sysconfdir}/rpmlint/config
%config(noreplace) %{_sysconfdir}/rpmlint/licenses.config
%config %{_sysconfdir}/rpmlint/rpmgroups.config
%config %{_sysconfdir}/rpmlint/pie.config
%dir %{_sysconfdir}/rpmlint
%doc %{_mandir}/man1/rpmlint.1.gz

