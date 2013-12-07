%define _with_bootstrap 0
%define bootstrap %{?_with_bootstrap:1}%{!?_with_bootstrap:%{?_without_bootstrap:0}%{!?_without_bootstrap:%{?_bootstrap:%{_bootstrap}}%{!?_bootstrap:0}}}

%define cvs_version %(echo %version |sed -e 's,\\\.,_,g')

Name:           xalan-j2
Version:        2.7.1
Release:        3
Epoch:          0
Summary:        Java XSLT processor
License:        Apache Software License
Source0:        http://archive.apache.org/dist/xml/xalan-j/source/xalan-j_%{cvs_version}-src.tar.gz
Patch0:         %{name}-noxsltcdeps.patch
Patch1:         %{name}-manifest.patch
Patch2:         %{name}-crosslink.patch
URL:            http://xalan.apache.org/
Group:          Development/Java
#Vendor:         JPackage Project
#Distribution:   JPackage
#BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildArch:      noarch
Provides:       jaxp_transform_impl
Requires:       jaxp_parser_impl
Requires(post):  update-alternatives
Requires(preun): update-alternatives
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  java-1.6.0-openjdk-devel java-rpmbuild
BuildRequires:  ant
%if ! %{bootstrap}
BuildRequires:  java_cup
BuildRequires:  bcel
BuildRequires:  jlex
BuildRequires:  regexp
BuildRequires:  sed
BuildRequires:  servletapi5
BuildRequires:  xerces-j2 >= 0:2.7.1
%endif
#BuildRequires:  xerces-j2 >= 0:2.7.1
BuildRequires:  xml-commons-jaxp-1.3-apis >= 0:1.3.03

%description
Xalan is an XSLT processor for transforming XML documents into HTML,
text, or other XML document types. It implements the W3C Recommendations
for XSL Transformations (XSLT) and the XML Path Language (XPath). It can
be used from the command line, in an applet or a servlet, or as a module
in other program.

%if ! %{bootstrap}
%package        xsltc
Summary:        XSLT compiler
Group:          Development/Java
Requires:       java_cup
Requires:       bcel
Requires:       jlex
Requires:       regexp
Requires:       jaxp_parser_impl

%description    xsltc
The XSLT Compiler is a Java-based tool for compiling XSLT stylesheets into
lightweight and portable Java byte codes called translets.
%endif

%package        manual
Summary:        Manual for %{name}
Group:          Development/Java

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
BuildRequires:  java-javadoc

%description    javadoc
Javadoc for %{name}.

%if ! %{bootstrap}
%package        demo
Summary:        Demo for %{name}
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}, servlet
BuildRequires:  servlet

%description    demo
Demonstrations and samples for %{name}.
%endif

%track
prog %name = {
	url = http://xalan.apache.org/xalan-j/index.html
	version = %version
	regex = "The current stable version for download is (__VER__)"
}

%prep
%setup -q -n xalan-j_%{cvs_version}
%apply_patches
# Remove all binary libs, except ones needed to build docs and N/A elsewhere.
for j in $(find . -name "*.jar"); do
        rm $j
done
# FIXME who knows where the sources are? xalan-j1 ?
#mv tools/xalan2jdoc.jar.no tools/xalan2jdoc.jar
#mv tools/xalan2jtaglet.jar.no tools/xalan2jtaglet.jar

%build
if [ ! -e "$JAVA_HOME" ] ; then export JAVA_HOME="%{java_home}" ; fi
pushd lib
ln -sf $(build-classpath java_cup-runtime) runtime.jar
ln -sf $(build-classpath bcel) BCEL.jar
ln -sf $(build-classpath regexp) regexp.jar
ln -sf $(build-classpath xerces-j2) xercesImpl.jar
ln -sf $(build-classpath xml-commons-jaxp-1.3-apis) xml-apis.jar
popd
pushd tools
ln -sf $(build-classpath java_cup) java_cup.jar
ln -sf $(build-classpath ant) ant.jar
ln -sf $(build-classpath jlex) JLex.jar
#ln -sf $(build-classpath xml-stylebook) stylebook-1.0-b3_xalan-2.jar
popd
export CLASSPATH=$(build-classpath servletapi5)
export JAVA_HOME=%_prefix/lib/jvm/java-1.6.0

%if %{bootstrap}
ant \
  -Djava.awt.headless=true \
  -Dapi.j2se=%{_javadocdir}/java \
  -Dbuild.xalan-interpretive.jar=build/xalan-interpretive.jar \
  xalan-interpretive.jar
%else
ant \
  -Djava.awt.headless=true \
  -Dapi.j2se=%{_javadocdir}/java \
  -Dbuild.xalan-interpretive.jar=build/xalan-interpretive.jar \
  xalan-interpretive.jar\
  xsltc.unbundledjar \
  docs \
  xsltc.docs \
  javadocs \
  samples \
  servlet
%endif

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 build/xalan-interpretive.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%if ! %{bootstrap}
install -p -m 644 build/xsltc.jar \
  $RPM_BUILD_ROOT%{_javadir}/xsltc-%{version}.jar
%endif
install -p -m 644 build/serializer.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-serializer-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%if ! %{bootstrap}

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
rm -rf build/docs/apidocs

# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m 644 build/xalansamples.jar \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-samples.jar
install -p -m 644 build/xalanservlet.war \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-servlet.war
cp -pr samples $RPM_BUILD_ROOT%{_datadir}/%{name}

# fix link between manual and javadoc
(cd build/docs; ln -sf %{_javadocdir}/%{name}-%{version} apidocs)

%endif

%if 0
# jaxp_transform_impl ghost symlink
ln -s %{_sysconfdir}/alternatives \
  $RPM_BUILD_ROOT%{_javadir}/jaxp_transform_impl.jar
%endif

%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
  jaxp_transform_impl %{_javadir}/%{name}.jar 30

%preun
{
  [ $1 = 0 ] || exit 0
  update-alternatives --remove jaxp_transform_impl %{_javadir}/%{name}.jar
} >/dev/null 2>&1 || :

#%post xsltc
#update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
#  jaxp_transform_impl %{_javadir}/xsltc.jar 10

#%preun xsltc
#{
#  [ $1 = 0 ] || exit 0
#  update-alternatives --remove jaxp_transform_impl %{_javadir}/xsltc.jar
#} >/dev/null 2>&1 || :

%if ! %{bootstrap}
%if 0
%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi
%endif
%endif

%files
%defattr(0644,root,root,0755)
%doc KEYS
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-serializer-%{version}.jar
%{_javadir}/%{name}-serializer.jar
%if 0
%ghost %{_javadir}/jaxp_transform_impl.jar
%endif

%if ! %{bootstrap}
%files xsltc
%defattr(0644,root,root,0755)
%{_javadir}/xsltc-%{version}.jar
%{_javadir}/xsltc.jar
#%ghost %{_javadir}/jaxp_transform_impl.jar

%files manual
%defattr(0644,root,root,0755)
%doc build/docs/*

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

%endif


%changelog
* Sat May 07 2011 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.0-7.0.10mdv2011.0
+ Revision: 671257
- mass rebuild

* Sat Dec 04 2010 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.0-7.0.9mdv2011.0
+ Revision: 608179
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.0-7.0.8mdv2010.1
+ Revision: 524371
- rebuilt for 2010.1

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0:2.7.0-7.0.7mdv2009.1
+ Revision: 351246
- rebuild

* Tue Jul 08 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.7.0-7.0.6mdv2009.0
+ Revision: 232661
- fix build, disable gcj_compile

* Thu Jan 10 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.7.0-7.0.5mdv2008.1
+ Revision: 147618
- full build

* Thu Jan 10 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.7.0-7.0.4mdv2008.1
+ Revision: 147597
- bootstrap

  + David Walluck <walluck@mandriva.org>
    - bump release

* Wed Dec 26 2007 David Walluck <walluck@mandriva.org> 0:2.7.0-7.0.2mdv2008.1
+ Revision: 137872
- rebuild

* Wed Dec 19 2007 David Walluck <walluck@mandriva.org> 0:2.7.0-7.0.1mdv2008.1
+ Revision: 133162
- BuildRequires: java-rpmbuild
- sync with jpackage
- don't %%ghost alternative link

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:2.7.0-2.8mdv2008.1
+ Revision: 121050
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

  + Thierry Vignaud <tv@mandriva.org>
    - kill file require on update-alternatives

* Wed Jul 18 2007 Anssi Hannula <anssi@mandriva.org> 0:2.7.0-2.7mdv2008.0
+ Revision: 53214
- use xml-commons-jaxp-1.3-apis explicitely instead of the generic
  xml-commons-apis which is provided by multiple packages (see bug #31473)


* Mon Nov 06 2006 David Walluck <walluck@mandriva.org> 2.7.0-2.6mdv2007.0
+ Revision: 76824
- rebuild

* Mon Nov 06 2006 David Walluck <walluck@mandriva.org> 0:2.7.0-2.5mdv2007.1
+ Revision: 76813
- set gcj_support to 0

* Sat Nov 04 2006 David Walluck <walluck@mandriva.org> 0:2.7.0-2.4mdv2007.1
+ Revision: 76457
- fix xml-commons-apis BuildRequires
- rebuild
- Import xalan-j2

* Sat Aug 26 2006 David Walluck <walluck@mandriva.org> 0:2.7.0-2.2mdv2007.0
- require latest xml-commons-apis
- fix some (Build)Requires
- fix ant -> %%ant

* Wed Jul 19 2006 David Walluck <walluck@mandriva.org> 0:2.7.0-2.1mdv2007.0
- release

* Sat Jun 03 2006 David Walluck <walluck@mandriva.org> 0:2.6.0-3.4.3mdv2007.0
- rebuild for libgcj.so.7
- fix macros

* Sat Mar 04 2006 Giuseppe Ghibò <ghibo@mandriva.com> 0:2.6.0-3.4.2mdk
- Use %%update_gcjdb.

* Sat Dec 03 2005 David Walluck <walluck@mandriva.org> 0:2.6.0-3.4.1mdk
- sync with 3jpp_4fc

* Sat Oct 29 2005 David Walluck <walluck@mandriva.org> 0:2.6.0-3.3.1mdk
- sync with 3jpp_3fc

* Sun May 22 2005 David Walluck <walluck@mandriva.org> 0:2.6.0-2.1mdk
- release

* Sat Apr 02 2005 Gary Benson <gbenson@redhat.com>
- Add NOTICE file as per Apache License version 2.0.

* Wed Jan 12 2005 Gary Benson <gbenson@redhat.com> 0:2.6.0-2jpp_1fc
- Sync with RHAPS.

* Mon Nov 15 2004 Fernando Nasser <fnasser@redhat.com> 0:2.6.0-2jpp_1rh
- Merge with latest community release

* Thu Nov 04 2004 Gary Benson <gbenson@redhat.com> 0:2.6.0-1jpp_2fc
- Build into Fedora.

* Fri Aug 27 2004 Ralph Apel <r.ape at r-apel.de> 0:2.6.0-2jpp
- Build with ant-1.6.2
- Try with -Djava.awt.headless=true

* Tue Mar 23 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2.6.0-1jpp
- Updated to 2.6.0 
- Patches supplied by <aleksander.adamowski@altkom.pl>

* Sat Nov 15 2003 Ville SkyttÃ¤ <ville.skytta at iki.fi> - 0:2.5.2-1jpp
- Update to 2.5.2.
- Re-enable javadocs, new style versionless symlink handling, crosslink
  with local J2SE javadocs.
- Spec cleanups.

