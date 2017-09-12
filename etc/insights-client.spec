%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define _binaries_in_noarch_packages_terminate_build 0

Name:                   insights-client
Summary:                Uploads Insights information to Red Hat on a periodic basis
Version:                2.0.5
Release:                13%{?dist}
Source0:                https://github.com/redhataccess/insights-client/archive/insights-client-%{version}.tar.gz
Epoch:                  0
License:                GPLv2+
URL:                    http://access.redhat.com/insights
Group:                  Applications/System
Vendor:                 Red Hat, Inc.

Provides: redhat-access-insights

Obsoletes: redhat-access-proactive
Obsoletes: redhat-access-insights

Requires: python
Requires: python-setuptools
Requires: python-requests >= 2.6
Requires: pyOpenSSL
Requires: libcgroup
Requires: tar
Requires: gpg
Requires: pciutils
%if 0%{?rhel} && 0%{?rhel} > 6
Requires: libcgroup-tools
%endif
BuildArch: noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Sends insightful information to Red Hat for automated analysis

%prep
%setup -q

%install
rm -rf ${RPM_BUILD_ROOT}
%{__python} setup.py install --root=${RPM_BUILD_ROOT} $PREFIX

%post
#Migrate existing machine-id
if  [ -f "/etc/redhat_access_proactive/machine-id" ]; then
mv /etc/redhat_access_proactive/machine-id /etc/insights-client/machine-id
fi
#Migrate OTHER existing machine-id
if [ -f "/etc/redhat-access-insights/machine-id" ]; then
mv /etc/redhat-access-insights/machine-id /etc/insights-client/machine-id
fi
#Migrate existing config
if [ -f "/etc/redhat-access-insights/redhat-access-insights.conf" ]; then
mv /etc/redhat-access-insights/redhat-access-insights.conf /etc/insights-client/insights-client.conf
sed -i 's/\[redhat-access-insights\]/\[insights-client\]/' /etc/insights-client/insights-client.conf
fi
#Migrate registration record
if [ -f "/etc/redhat-access-insights/.registered" ]; then
mv /etc/redhat-access-insights/.registered /etc/insights-client/.registered
fi
#Migrate last upload record
if [ -f "/etc/redhat-access-insights/.lastupload" ]; then
mv /etc/redhat-access-insights/.lastupload /etc/insights-client/.lastupload
fi
# Create symlinks to old name
ln -sf %{_bindir}/insights-client %{_bindir}/redhat-access-insights
if ! [ -d "/etc/redhat-access-insights" ]; then
mkdir /etc/redhat-access-insights
fi
ln -sf /etc/insights-client/insights-client.conf /etc/redhat-access-insights/redhat-access-insights.conf
ln -sf /etc/insights-client/insights-client.cron /etc/redhat-access-insights/redhat-access-insights.cron
ln -sf /etc/cron.daily/insights-client /etc/cron.daily/redhat-access-insights
ln -sf /etc/cron.weekly/insights-client /etc/cron.weekly/redhat-access-insights
ln -sf /etc/insights-client/.registered /etc/redhat-access-insights/.registered
ln -sf /etc/insights-client/.unregistered /etc/redhat-access-insights/.unregistered
ln -sf /etc/insights-client/machine-id /etc/redhat-access-insights/machine-id

%postun
if [ "$1" -eq 0 ]; then
rm -f /etc/cron.daily/insights-client
rm -f /etc/cron.weekly/insights-client
rm -f /etc/insights-client/.cache*
rm -f /etc/insights-client/.registered
rm -f /etc/insights-client/.unregistered
rm -f /etc/insights-client/.lastupload
# remove symlink to old name on uninstall
rm -f %{_bindir}/redhat-access-insights
# remove symlinks to old configs
rm -rf /etc/redhat-access-insights/
rm -f /etc/cron.daily/redhat-access-insights
rm -f /etc/cron.weekly/redhat-access-insights
fi

%clean
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT

%files
%defattr(755,root,root)
%{_bindir}/insights-client
/etc/insights-client/insights-client.cron
/etc/insights-client/insights-client-container.cron

%defattr(0600, root, root)
%dir /etc/insights-client
%config(noreplace) /etc/insights-client/*.conf
/etc/insights-client/.fallback.json
/etc/insights-client/.fallback.json.asc
/etc/insights-client/redhattools.pub.gpg
/etc/insights-client/.exp.sed
/etc/insights-client/*.pem

%defattr(-,root,root)
%{python_sitelib}/insights_client*.egg-info
%{python_sitelib}/insights_client/*.py*
%{_sharedstatedir}/insights_client/insights-client-*.tar.gz

%doc
/usr/share/man/man8/*.8.gz
/usr/share/man/man5/*.5.gz

%changelog
* Tue Sep 12 2017 Richard Brantley <rbrantle@redhat.com> - 2.0.5-13
- Resolves: bz1490450
- Fixes proxy hostname validation issues

* Tue Jan 17 2017 Richard Brantley <rbrantle@redhat.com> - 2.0.5-5
- Updates some man page verbiage
- Displays error messages and status codes from API
- Fixes traceback on improper API response
- Include build number in version output for support

* Wed Jan 11 2017 Richard Brantley <rbrantle@redhat.com> - 2.0.5-4
- Adds Machine ID and Acccount Numbers to STDOUT and logs

* Fri Jan 6 2017 Richard Brantley <rbrantle@redhat.com> - 2.0.5-3
- Fixes subscription manager host issues
- Adds command timeouts
- Fixes no_proxy base url

* Fri Aug 26 2016 Jeremy Crafts <jcrafts@redhat.com> - 2.0.4-0
- Rename to insights-client, refactor some things
- Handle container-based collection
- Misc bugfixes
- Resolves: bz1320581, bz1323150, bz1323187, bz1325111

* Fri Mar 18 2016 Jeremy Crafts <jcrafts@redhat.com> - 1.0.8-7
- Fix bugs related to --from-stdin and --to-stdout options
- Resolves: bz1319015

* Fri Mar 04 2016 Jeremy Crafts <jcrafts@redhat.com> - 1.0.8-0
- Fix scheduling-related issues
- Add status check for registration with API
- Fix connectivity bug
- Improved debug messaging
- Resolves: bz1257238, bz1267303, bz1268002, bz1276058, bz1295928, bz1295931, bz1295932, bz1295934, bz1295940, bz1310242, bz1310243

* Wed Jan 06 2016 Jeremy Crafts <jcrafts@redhat.com> - 1.0.7-3
- New config options trace and no_schedule
- New command line options --no_schedule, --conf, --to-stdout, --compressor, --from-stdin, --support, --offline, and --status
- Add certificate chain verification to connection test
- Revised debug output
- Reduced set of environment vars used for command execution
- OpenStack cluster support
- Remember time of last successful upload
- Resolves: bz1237112, bz1243028, bz1244113, bz1246919, bz1250384, bz1257242, bz1267299, bz1276055, bz1276130, bz1280353, bz1295929, bz1295935, bz1295939 

* Tue Aug 11 2015 Dan Varga <dvarga@redhat.com> - 1.0.6-0
- Fix unregister -> reregister flow
- Resolves: bz1252435

* Wed Jul 29 2015 Dan Varga <dvarga@redhat.com> - 1.0.5-0
- Automatically retry failed uploads when invoked via cron
- Update python-requests dependency to >= 2.6
- Add --unregister option
- --no-gpg fix
- Remove --weekly option
- Add --quiet and --silent options
- Default cron to quiet
- Fix satellite 5 proxy auto configuration
- Remove .registered and .unregistered files on uninstallation
- lowercase -> lower()
- Resolves: bz1248011, bz1248012, bz1248014, bz1248023

* Mon Jun 08 2015 Dan Varga <dvarga@redhat.com> - 1.0.4-0
- Improved logging of exceptions
- Redact passwords automatically

* Mon Jun 01 2015 Dan Varga <dvarga@redhat.com> - 1.0.3-0
- New default URLs
- New config file format
- Default to auto configuration

* Mon May 18 2015 Dan Varga <dvarga@redhat.com> - 1.0.2-0
- Update man pages

* Thu May 07 2015 Dan Varga <dvarga@redhat.com> - 1.0.1-0
- Add man pages
- New certificate chain for cert-api.access.redhat.com
- Better auto configuration for satellite installations

* Wed Apr 29 2015 Dan Varga <dvarga@redhat.com> - 1.0.0-2
- Drop min python-requests version to 2.4

* Mon Apr 27 2015 Dan Varga <dvarga@redhat.com> - 1.0.0-1
- Add LICENSE file
- Resolves: bz1215002

* Thu Apr 23 2015 Dan Varga <dvarga@redhat.com> - 1.0.0-0
- Initial build
- Resolves: bz1176237
