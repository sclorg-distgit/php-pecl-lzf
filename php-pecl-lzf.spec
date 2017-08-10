# centos/sclo spec file for php-pecl-lzf, from:
#
# remirepo spec file for php-pecl-lzf
# adapted for SCL, from
#
# Fedora spec file for php-pecl-lzf
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#
%if 0%{?scl:1}
%global sub_prefix sclo-%{scl_prefix}
%if "%{scl}" == "rh-php56"
%global sub_prefix sclo-php56-
%endif
%if "%{scl}" == "rh-php70"
%global sub_prefix sclo-php70-
%endif
%if "%{scl}" == "rh-php71"
%global sub_prefix sclo-php71-
%endif
%scl_package        php-pecl-lzf
%endif

%define pecl_name   LZF
%define  ext_name   lzf
%global ini_name    40-%{ext_name}.ini

Name:           %{?sub_prefix}php-pecl-lzf
Version:        1.6.5
Release:        2%{?dist}
Summary:        Extension to handle LZF de/compression
Group:          Development/Languages
# extension is PHP, lzf library is BSD
License:        PHP and BSD
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  %{?scl_prefix}php-pear

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}

Provides:       %{?scl_prefix}php-%{ext_name}                = %{version}
Provides:       %{?scl_prefix}php-%{ext_name}%{?_isa}        = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:       %{?scl_prefix}php-pecl-%{ext_name}           = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-%{ext_name}%{?_isa}   = %{version}-%{release}
%endif
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This extension provides LZF compression and decompression using the liblzf
library.

LZF is a very fast compression algorithm, ideal for saving space with a 
slight speed cost.

Documentation: http://php.net/lzf

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%prep
%setup -c -q

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

mv %{pecl_name}-%{version} NTS
cd NTS
%{?_licensedir:mv lib/LICENSE LICENSE.lzf}

extver=$(sed -n '/#define PHP_LZF_VERSION/{s/.* "//;s/".*$//;p}' php_lzf.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

cat >%{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=lzf.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --enable-lzf \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make install -C NTS INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Documentation
cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}/%{php_extdir}/%{ext_name}.so \
    --modules | grep -i %{ext_name}

TEST_PHP_EXECUTABLE=%{__php} \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
%{__php} -n run-tests.php \
    -n -q \
    -d extension=%{buildroot}%{php_extdir}/%{ext_name}.so


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%{?_licensedir:%license NTS/LICENSE*}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{ext_name}.so


%changelog
* Thu Aug 10 2017 Remi Collet <remi@remirepo.net> - 1.6.5-2
- change for sclo-php71

* Fri Nov 11 2016 Remi Collet <remi@fedoraproject.org> - 1.6.5-1
- cleanup for SCLo build
- use bundled lzf library

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 1.6.5-2
- rebuild for PHP 7.1 new API version

* Sun Apr  3 2016 Remi Collet <remi@fedoraproject.org> - 1.6.5-1
- update to 1.6.5 (stable)

* Sat Apr  2 2016 Remi Collet <remi@fedoraproject.org> - 1.6.4-1
- update to 1.6.4 (stable)

* Sun Mar  6 2016 Remi Collet <remi@fedoraproject.org> - 1.6.3-7
- adapt for F24

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-6
- rebuild for PHP 7.0.0RC5 new API version

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-5
- F23 rebuild with rh_layout

* Wed Jul 22 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-4
- rebuild against php 7.0.0beta2

* Wed Jul  8 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-3
- rebuild against php 7.0.0beta1

* Fri Jun 19 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-2
- allow build against rh-php56 (as more-php56)
- rebuild for "rh_layout" (php70)

* Mon Apr 20 2015 Remi Collet <remi@fedoraproject.org> - 1.6.3-1
- update to 1.6.3

* Sat Apr  4 2015 Remi Collet <remi@fedoraproject.org> - 1.6.2-11
- add upstream fix for PHP 7
- fix license handling
- don't install/register tests
- drop runtime dependency on pear, new scriptlets

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.6.2-10.1
- Fedora 21 SCL mass rebuild

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 1.6.2-10
- improve SCL build

* Wed Apr 16 2014 Remi Collet <remi@fedoraproject.org> - 1.6.2-9
- add numerical prefix to extension configuration file

* Wed Mar 19 2014 Remi Collet <remi@fedoraproject.org> - 1.6.2-8
- allow SCL build

* Mon Mar 10 2014 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-7
- cleanups for Copr

* Fri Feb 28 2014 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-6
- cleanups
- move doc in pecl_docdir
- move tests in pecl_docdir
- add missing LICENSE file

* Fri Nov 30 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-2.1
- also provides php-lzf

* Sun Oct 21 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-2
- sync with rawhide (use system liblzf)

* Sat Oct 20 2012 Andrew Colin Kissa - 1.6.2-1
- Upgrade to latest upstream
- Fix bugzilla #838309 #680230

* Mon Jul 09 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-1
- update to 1.6.2

* Sat Jul 07 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.6.1-1
- update to 1.6.1

* Fri Nov 18 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.5.2-8
- php 5.4 build

* Sat Oct 15 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.5.2-7
- zts extension
- spec cleanup

* Fri Jul 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-7
- Fix bugzilla #715791

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 1.5.2-4
- rebuild for new PHP 5.3.0 ABI (20090626)

* Mon Jun 22 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-3
- Consistent use of macros

* Mon Jun 22 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-2
- Fixes to the install to retain timestamps and other fixes raised in review

* Sun Jun 14 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-1
- Initial RPM package
