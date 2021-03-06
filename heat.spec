Name: heat
Summary: This software provides AWS CloudFormation functionality for OpenStack Essex
Version: 6
Release: 3%{?dist}
License: ASL 2.0
Group: System Environment/Base
URL: http://heat-api.org
Source0: https://github.com/downloads/heat-api/heat/heat-%{version}.tar.gz
Source1: heat.logrotate
Source2: heat-api.service
Source3: heat-engine.service
Source4: heat-metadata.service

# fedora specific patches commented out
#Patch0: switch-to-using-m2crypto.patch

BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: systemd-units

Requires: python-eventlet
Requires: python-glance
Requires: python-greenlet
Requires: python-httplib2
Requires: python-iso8601
Requires: python-keystoneclient
Requires: python-kombu
Requires: python-lxml
Requires: python-memcached
Requires: python-migrate
Requires: python-novaclient
Requires: python-paste
Requires: python-qpid
Requires: python-routes
Requires: pysendfile
Requires: python-sqlalchemy
Requires: python-webob

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(pre): shadow-utils

%prep
%setup -q
#%%patch0 -p1

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root=$RPM_BUILD_ROOT
sed -i -e '/^#!/,1 d' $RPM_BUILD_ROOT/%{python_sitelib}/heat/db/sqlalchemy/manage.py
sed -i -e '/^#!/,1 d' $RPM_BUILD_ROOT/%{python_sitelib}/heat/db/sqlalchemy/migrate_repo/manage.py
sed -i -e '/^#!/,1 d' $RPM_BUILD_ROOT/%{python_sitelib}/heat/testing/runner.py
mkdir -p $RPM_BUILD_ROOT/var/log/heat/
install -p -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/heat

# install systemd unit files
install -p -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/heat-api.service
install -p -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}/heat-engine.service
install -p -D -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/heat-metadata.service

mkdir -p $RPM_BUILD_ROOT/var/lib/heat/
mkdir -p $RPM_BUILD_ROOT/etc/heat/
cp -r etc/* $RPM_BUILD_ROOT/etc/heat/
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1/
cp -v docs/man/man1/* $RPM_BUILD_ROOT/%{_mandir}/man1/
rm -rf $RPM_BUILD_ROOT/var/lib/heat/.dummy

%description
Heat provides AWS CloudFormation functionality for OpenStack.

%files
%doc README.rst LICENSE
%{_mandir}/man1/*.gz
%{_bindir}/*
%{python_sitelib}/heat*
%dir %attr(0755,heat,root) %{_localstatedir}/log/heat
%dir %attr(0755,heat,root) %{_localstatedir}/lib/heat
%{_unitdir}/heat*.service
%dir %{_sysconfdir}/heat
%config(noreplace) %{_sysconfdir}/logrotate.d/heat
%config(noreplace) %{_sysconfdir}/heat/bash_completion.d/heat
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-api-paste.ini
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-api.conf
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-engine-paste.ini
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-engine.conf
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-metadata-paste.ini
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/heat-metadata.conf
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/boto.cfg

%pre
getent group openstack-heat >/dev/null || groupadd -r openstack-heat
getent passwd openstack-heat  >/dev/null || \
useradd -r -g openstack-heat -d %{_localstatedir}/lib/heat -s /sbin/nologin \
    -c "OpenStack Heat Daemon" openstack-heat
exit 0

%post
%systemd_post heat-api.service
%systemd_post heat-engine.service
%systemd_post heat-metadata.service

%preun
%systemd_preun heat-api.service
%systemd_preun heat-engine.service
%systemd_preun heat-engine.service

%postun
%systemd_postun_with_restart heat-api.service
%systemd_postun_with_restart heat-engine.service
%systemd_postun_with_restart heat-metadata.service

%changelog
* Tue Aug 21 2012 Jeff Peeler <jpeeler@redhat.com> 6-3
- updated systemd scriptlets

* Tue Aug  7 2012 Jeff Peeler <jpeeler@redhat.com> 6-2
- change user/group ids to openstack-heat

* Wed Aug 1 2012 Jeff Peeler <jpeeler@redhat.com> 6-1
- create heat user and change file permissions
- set systemd scripts to run as heat user

* Fri Jul 27 2012 Ian Main <imain@redhat.com> - 5-1
- added m2crypto patch.
- bumped version for new release.
- added boto.cfg to sysconfigdir

* Tue Jul 24 2012 Jeff Peeler <jpeeler@redhat.com> - 4-5
- added LICENSE to docs
- added dist tag
- added heat directory to files section
- removed unnecessary defattr 

* Tue Jul 24 2012 Jeff Peeler <jpeeler@redhat.com> - 4-4
- remove pycrypto requires

* Fri Jul 20 2012 Jeff Peeler <jpeeler@redhat.com> - 4-3
- change python-devel to python2-devel

* Wed Jul 11 2012 Jeff Peeler <jpeeler@redhat.com> - 4-2
- add necessary requires
- removed shebang line for scripts not requiring executable permissions
- add logrotate, removes all rpmlint warnings except for python-httplib2
- remove buildroot tag since everything since F10 has a default buildroot
- remove clean section as it is not required as of F13
- add systemd unit files
- change source URL to download location which doesn't require a SHA

* Fri Jun 8 2012 Steven Dake <sdake@redhat.com> - 4-1
- removed jeos from packaging since that comes from another repository
- compressed all separate packages into one package
- removed setup options which were producing incorrect results
- replaced python with {__python}
- added a br on python-devel
- added a --skip-build to the install step
- added percent-dir for directories
- fixed most rpmlint warnings/errors

* Mon Apr 16 2012 Chris Alfonso <calfonso@redhat.com> - 3-1
- initial openstack package log
