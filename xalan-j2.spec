%{?_javapackages_macros:%_javapackages_macros}
# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%global cvs_version 2_7_1

Name:           xalan-j2
Version:        2.7.1
Release:        21.1%{?dist}
Epoch:          0
Summary:        Java XSLT processor
# src/org/apache/xpath/domapi/XPathStylesheetDOM3Exception.java is W3C
License:        ASL 2.0 and W3C
Source0:        http://archive.apache.org/dist/xml/xalan-j/xalan-j_2_7_1-src.tar.gz
Source1:        %{name}-serializer-MANIFEST.MF
Source2:        http://repo1.maven.org/maven2/xalan/xalan/2.7.1/xalan-2.7.1.pom
Source3:        http://repo1.maven.org/maven2/xalan/serializer/2.7.1/serializer-2.7.1.pom
Source4:        xsltc-%{version}.pom
Source5:        %{name}-MANIFEST.MF
Patch0:         %{name}-noxsltcdeps.patch
# Fix the serializer JAR filename in xalan-j2's MANIFEST.MF
# https://bugzilla.redhat.com/show_bug.cgi?id=718738
Patch1:         %{name}-serializerJARname.patch
URL:            http://xalan.apache.org/


BuildArch:      noarch
Provides:       jaxp_transform_impl
Requires:       xerces-j2
Requires(post): chkconfig
Requires(preun): chkconfig
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  java-devel
BuildRequires:  ant
BuildRequires:  bcel
BuildRequires:  java_cup
BuildRequires:  regexp
BuildRequires:  sed
BuildRequires:  tomcat-servlet-3.0-api
BuildRequires:  xerces-j2 >= 0:2.7.1
BuildRequires:  xml-commons-apis >= 0:1.3
BuildRequires:  xml-stylebook
BuildRequires:  zip

%description
Xalan is an XSLT processor for transforming XML documents into HTML,
text, or other XML document types. It implements the W3C Recommendations
for XSL Transformations (XSLT) and the XML Path Language (XPath). It can
be used from the command line, in an applet or a servlet, or as a module
in other program.

%package        xsltc
Summary:        XSLT compiler

Requires:       java_cup
Requires:       bcel
Requires:       regexp
Requires:       xerces-j2

%description    xsltc
The XSLT Compiler is a Java-based tool for compiling XSLT stylesheets into
lightweight and portable Java byte codes called translets.

%package        manual
Summary:        Manual for %{name}


%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}

Requires:       jpackage-utils
BuildRequires:  java-javadoc

%description    javadoc
Javadoc for %{name}.

%package        demo
Summary:        Demo for %{name}

Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       tomcat-servlet-3.0-api

%description    demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n xalan-j_%{cvs_version}
%patch0 -p0
%patch1 -p0
# Remove all binary libs, except ones needed to build docs and N/A elsewhere.
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done

# this tar.gz contains bundled software, some of which has unclear
# licensing terms (W3C Software/Document license) . We could probably
# replicate this with our jars but it's too much work so just generate
# non-interlinked documentation
rm src/*tar.gz
sed -i '/<!-- Expand jaxp sources/,/<delete file="${xml-commons-srcs.tar}"/{d}' build.xml

# FIXME who knows where the sources are? xalan-j1 ?
mv tools/xalan2jdoc.jar.no tools/xalan2jdoc.jar
mv tools/xalan2jtaglet.jar.no tools/xalan2jtaglet.jar

# Remove classpaths from manifests
sed -i '/class-path/I d' $(find -iname *manifest*)

# Convert CR-LF to LF-only
sed -i s/// KEYS LICENSE.txt NOTICE.txt

%build
if [ ! -e "$JAVA_HOME" ] ; then export JAVA_HOME="%{java_home}" ; fi
pushd lib
ln -sf $(build-classpath java_cup-runtime) runtime.jar
ln -sf $(build-classpath bcel) BCEL.jar
ln -sf $(build-classpath regexp) regexp.jar
ln -sf $(build-classpath xerces-j2) xercesImpl.jar
ln -sf $(build-classpath xml-commons-apis) xml-apis.jar
popd
pushd tools
ln -sf $(build-classpath java_cup) java_cup.jar
ln -sf $(build-classpath ant) ant.jar
ln -sf $(build-classpath xml-stylebook) stylebook-1.0-b3_xalan-2.jar
popd
export CLASSPATH=$(build-classpath servlet)

ant \
  -Djava.awt.headless=true \
  -Dapi.j2se=%{_javadocdir}/java \
  -Dbuild.xalan-interpretive.jar=build/xalan-interpretive.jar \
  xalan-interpretive.jar\
  xsltc.unbundledjar \
  docs \
  javadocs \
  samples \
  servlet


%install
# inject OSGi manifests
mkdir -p META-INF
cp -p %{SOURCE1} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u build/serializer.jar META-INF/MANIFEST.MF
cp -p %{SOURCE5} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u build/xalan-interpretive.jar META-INF/MANIFEST.MF

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 build/xalan-interpretive.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
install -p -m 644 build/xsltc.jar \
  $RPM_BUILD_ROOT%{_javadir}/xsltc.jar
install -p -m 644 build/serializer.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-serializer.jar

# POMs
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}-serializer.pom
install -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-xsltc.pom
%add_maven_depmap JPP-%{name}.pom %{name}.jar
%add_maven_depmap JPP-%{name}-serializer.pom %{name}-serializer.jar
%add_maven_depmap -f xsltc JPP-xsltc.pom xsltc.jar

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr build/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}
rm -rf build/docs/apidocs

# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m 644 build/xalansamples.jar \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-samples.jar
install -p -m 644 build/xalanservlet.war \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-servlet.war
cp -pr samples $RPM_BUILD_ROOT%{_datadir}/%{name}

# fix link between manual and javadoc
(cd build/docs; ln -sf %{_javadocdir}/%{name} apidocs)

# jaxp_transform_impl ghost symlink
ln -s %{_sysconfdir}/alternatives \
  $RPM_BUILD_ROOT%{_javadir}/jaxp_transform_impl.jar


%post
update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
  jaxp_transform_impl %{_javadir}/%{name}.jar 30

%preun
{
  [ $1 = 0 ] || exit 0
  update-alternatives --remove jaxp_transform_impl %{_javadir}/%{name}.jar
} >/dev/null 2>&1 || :

%files -f .mfiles
%doc KEYS LICENSE.txt NOTICE.txt readme.html
%ghost %{_javadir}/jaxp_transform_impl.jar

%files xsltc -f .mfiles-xsltc
%doc LICENSE.txt NOTICE.txt

%files manual
%doc LICENSE.txt NOTICE.txt
%doc build/docs/*

%files javadoc
%doc LICENSE.txt NOTICE.txt
%doc %{_javadocdir}/%{name}

%files demo
%{_datadir}/%{name}

%changelog
* Mon Aug 19 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.1-21
- Move depmaps to appropriate packages
- Resolves: rhbz#998594

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 10 2013 Krzysztof Daniel <kdaniel@redhat.com> 0:2.7.1-19
- Add export packages from Eclipse orbit.
- Restore dependency to system.bundle.

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Oct 12 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.1-17
- Remove classpaths from manifests, resolves: rhbz#575635
- Remove jlex from classpath
- Fix source URL to archive.apache.org
- Don't mix spaces and tabs in spec file
- Fix end-of-line encoding of some documentation files

* Fri Aug 24 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:2.7.1-16
- No more ASL 1.1 code present in the package, fix license

* Thu Aug 23 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:2.7.1-15
- Add NOTICE.txt file to subpackages
- Remove bundled sources of other packages used to build javadocs

* Thu Aug 16 2012 Andy Grimm <agrimm@gmail.com> - 0:2.7.1-14
- Remove osgi(system.bundle) requirement

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 12 2012 Andy Grimm <agrimm@gmail.com> - 0:2.7.1-12
- Change javax.servlet requirement to use tomcat 7

* Mon Jul 02 2012 Gerard Ryan <galileo@fedoraproject.org> - 0:2.7.1-11
- Fix Requires for javax.servlet to geronimo-osgi-support

* Sun Jun 24 2012 Gerard Ryan <galileo@fedoraproject.org> - 0:2.7.1-10
- Inject OSGI Manifest for xalan-j2.jar

* Tue May 29 2012 Andy Grimm <agrimm@gmail.com> - 0:2.7.1-9
- Follow new guidelines for EE API deps (#819546)

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Oct 10 2011 Andy Grimm <agrimm@gmail.com> 0:2.7.1-7
- add POM files

* Wed Aug 10 2011 Andrew Overholt <overholt@redhat.com> 0:2.7.1-6
- Fix filename of serializer.jar in xalan-j2's MANIFEST.MF
- https://bugzilla.redhat.com/show_bug.cgi?id=718738

* Tue Jul 26 2011 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.1-5
- Remove old commented parts.
- Fix rpmlint warnings.

* Tue Jun 28 2011 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.1-4
- Fix FTBFS.

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec 16 2010 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.1-2
- Update to current guidelines.

* Wed Apr 7 2010 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.1-1
- Update to 2.7.1.
- Drop gcj_support.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.0-9.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.0-8.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 3 2009 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.0-7.5
- Add osgi manifest.

* Sat Sep  6 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0:2.7.0-7.4
- fix license tag

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:2.7.0-7.3
- drop repotag
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:2.7.0-7jpp.2
- Autorebuild for GCC 4.3

* Fri Apr 20 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-6jpp.2.fc7
- Rebuild to fix incomplete .db/so files due to broken aot-compile-rpm

* Fri Aug 18 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-6jpp.1
- Resync with latest from JPP.

* Fri Aug 11 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-5jpp.3
- Rebuild.

* Thu Aug 10 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-5jpp.2
- Rebuild.

* Thu Aug 10 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-5jpp.1
- Resync with latest from JPP.
- Partially adopt new naming convention (.1 suffix).
- Use ln and rm explicitly instead of core-utils in Requires(x).

* Thu Aug 10 2006 Karsten Hopp <karsten@redhat.de> 2.7.0-4jpp_5fc
- Requires(post):     coreutils

* Wed Jul 26 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-4jpp_4fc
- Extend patch to cover all applicable MANIFEST files in src directory.

* Wed Jul 26 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-4jpp_3fc
- Apply patch to replace serializer.jar in MANIFEST file with
  xalan-j2-serializer.jar.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:2.7.0-4jpp_2fc
- Rebuilt

* Fri Jul 21 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-4jpp_1fc
- Resync with latest JPP version.

* Wed Jul 19 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:2.7.0-3jpp_1fc
- Merge with latest version from jpp.
- Undo ExcludeArch since eclipse available for all arch-es.
- Remove jars from sources for new upstream version.
- Purge unused patches from previous release.
- Conditional native compilation with GCJ.
- Use NVR macros wherever possible.

* Wed Mar  8 2006 Rafael Schloming <rafaels@redhat.com> - 0:2.6.0-3jpp_10fc
- excluded s390[x] and ppc64 due to eclipse

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:2.6.0-3jpp_9fc
- stop scriptlet spew

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:2.6.0-3jpp_8fc
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0:2.6.0-3jpp_7fc
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:2.6.0-3jpp_6fc
- rebuild again

* Tue Dec 13 2005 Jesse Keating <jkeating@redhat.com> 0:2.6.0-3jpp_5fc.3
- patch to not use target= in build.xml

* Tue Dec 13 2005 Jesse Keating <jkeating@redhat.com> 0:2.6.0-3jpp_5fc.1
- rebuild again with gcc-4.1

* Fri Dec 09 2005 Warren Togami <wtogami@redhat.com> 0:2.6.0-3jpp_5fc
- rebuild with gcc-4.1

* Tue Nov  1 2005 Archit Shah <ashah at redhat.com> 0:2.6.0-3jpp_4fc
- Exclude war which blocks aot compilation of main jar (#171005).

* Tue Jul 19 2005 Gary Benson <gbenson at redhat.com> 0:2.6.0-3jpp_3fc
- Build on ia64, ppc64, s390 and s390x.
- Switch to aot-compile-rpm (also BC-compiles xsltc and samples).

* Tue Jun 28 2005 Gary Benson <gbenson at redhat.com> 0:2.6.0-3jpp_2fc
- Remove a tarball from the tarball too.
- Fix demo subpackage's dependencies.

* Wed Jun 15 2005 Gary Benson <gbenson at redhat.com> 0:2.6.0-3jpp_1fc
- Remove jarfiles from the tarball.

* Fri May 27 2005 Gary Benson <gbenson at redhat.com> 0:2.6.0-3jpp
- Add NOTICE file as per Apache License version 2.0.
- Build with servletapi5.

* Fri May 27 2005 Gary Benson <gbenson@redhat.com> 0:2.6.0-2jpp_3fc
- Remove now-unnecessary workaround for #130162.
- Rearrange how BC-compiled stuff is built and installed.

* Tue May 24 2005 Gary Benson <gbenson@redhat.com> 0:2.6.0-2jpp_2fc
- Add DOM3 stubs to classes that need them (#152255).
- BC-compile the main jarfile.

* Fri Apr  1 2005 Gary Benson <gbenson@redhat.com>
- Add NOTICE file as per Apache License version 2.0.

* Wed Jan 12 2005 Gary Benson <gbenson@redhat.com> 0:2.6.0-2jpp_1fc
- Sync with RHAPS.

* Mon Nov 15 2004 Fernando Nasser <fnasser@redhat.com> 0:2.6.0-2jpp_1rh
- Merge with latest community release

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> 0:2.6.0-1jpp_2fc
- Build into Fedora.

* Thu Aug 26 2004 Ralph Apel <r.ape at r-apel.de> 0:2.6.0-2jpp
- Build with ant-1.6.2
- Try with -Djava.awt.headless=true

* Mon Jul 26 2004 Fernando Nasser <fnasser@redhat.com> 0:2.6.0-1jpp_1rh
- Merge with latest community version

* Fri Mar 26 2004 Frank Ch. Eigler <fche@redhat.com> 0:2.5.2-1jpp_2rh
- add RHUG upgrade cleanup

* Tue Mar 23 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2.6.0-1jpp
- Updated to 2.6.0
- Patches supplied by <aleksander.adamowski@altkom.pl>

* Thu Mar  4 2004 Frank Ch. Eigler <fche@redhat.com> - 0:2.5.2-1jpp_1rh
- RH vacuuming

* Sat Nov 15 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.5.2-1jpp
- Update to 2.5.2.
- Re-enable javadocs, new style versionless symlink handling, crosslink
  with local J2SE javadocs.
- Spec cleanups.

* Sat Jun  7 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.5.1-1jpp
- Update to 2.5.1.
- Fix jpackage-utils version in BuildRequires, add xerces-j2.
- Non-versioned javadoc symlinking.
- Add one missing epoch.
- Clean up manifests from Class-Path's and other stuff we don't include.
- xsltc no longer provides a jaxp_transform_impl because of huge classpath
  and general unsuitablity for production-use, system-installed transformer.
- Own (ghost) %%{_javadir}/jaxp_transform_impl.jar.
- Remove alternatives in preun instead of postun.
- Disable javadoc subpackage for now:
  <http://issues.apache.org/bugzilla/show_bug.cgi?id=20572>

* Thu Mar 27 2003 Nicolas Mailhot <Nicolas.Mailhot@One2team.com> 0:2.5.0.d1-1jpp
- For jpackage-utils 1.5

* Wed Jan 22 2003 Ville Skyttä <ville.skytta at iki.fi> - 2.4.1-2jpp
- bsf -> oldbsf.
- Use non-versioned jar in alternative, don't remove it on upgrade.
- Remove hardcoded packager tag.

* Mon Nov 04 2002 Henri Gomez <hgomez@users.sourceforge.net> 2.4.1-1jpp
- 2.4.1

* Tue Sep 10 2002 Ville Skyttä <ville.skytta at iki.fi> 2.4.0-1jpp
- 2.4.0.

* Thu Aug 22 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.4-0.D1.3jpp
- corrected case for Group tag
- fixed servlet classpath

* Tue Aug 20 2002 Ville Skyttä <ville.skytta at iki.fi> 2.4-0.D1.2jpp
- Remove xerces-j1 runtime dependency.
- Add bcel, jlex, regexp to xsltc runtime requirements:
  <http://xml.apache.org/xalan-j/xsltc_usage.html>
- Build with -Dbuild.compiler=modern (IBM 1.3.1) to avoid stylebook errors.
- XSLTC now provides jaxp_transform_impl too.
- Earlier changes by Henri, from unreleased 2.4-D1.1jpp:
    Mon Jul 15 2002 Henri Gomez <hgomez@users.sourceforge.net> 2.4-D1.1jpp
  - 2.4D1
  - use the jlex 1.2.5-5jpp (patched by Xalan/XSLTC team) rpm
  - use the stylebook-1.0-b3_xalan-2.jar included in source file till it will
    be packaged in jpackage
  - use jaxp_parser_impl (possibly xerces-j2) instead of xerces-j1 for docs
    generation, since it's tuned for stylebook-1.0-b3_xalan-2.jar
  - build and provide xsltc in a separate rpm

* Mon Jul 01 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.3.1-2jpp
- provides jaxp_transform_impl
- requires jaxp_parser_impl
- stylebook already requires xml-commons-apis
- jaxp_parser_impl already requires xml-commons-apis
- use sed instead of bash 2.x extension in link area to make spec compatible with distro using bash 1.1x

* Wed Jun 26 2002 Henri Gomez <hgomez@users.sourceforge.net> 2.3.1-2jpp
- fix built classpath (bsf, bcel are existing jpackage rpms),
- add buildrequires for javacup and JLex

* Wed May 08 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.3.1-1jpp
- 2.3.1
- vendor, distribution, group tags

* Mon Mar 18 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.3.0-2jpp
- generic servlet support

* Wed Feb 20 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.3.0-1jpp
- 2.3.0
- no more compat jar

* Sun Jan 27 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.0-2jpp
- adaptation to new stylebook1.0b3 package
- used source tarball
- section macro

* Fri Jan 18 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.0-1jpp
- 2.2.0 final
- versioned dir for javadoc
- no dependencies for manual and javadoc packages
- stricter dependency for compat and demo packages
- fixed package confusion
- adaptation for new servlet3 package
- requires xerces-j1 instead of jaxp_parser
- xml-apis jar now in required xml-commons-apis external package

* Wed Dec 5 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D14-1jpp
- 2.2.D14
- javadoc into javadoc package
- compat.jar into compat package
- compat javadoc into compat-javadoc package

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 2.2.D13-2jpp
- changed extension to jpp
- prefixed xml-apis

* Tue Nov 20 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 2.2.D13-1jpp
- 2.2.D13
- removed packager tag

* Sat Oct 6 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D11-1jpp
- 2.2.D11

* Sun Sep 30 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D10-2jpp
- first unified release
- s/jPackage/JPackage

* Fri Sep 14 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D10-1mdk
- cvs references
- splitted demo package
- moved demo files to %%{_datadir}/%%{name}
- only manual package requires stylebook-1.0b3
- only demo package requires servletapi3

* Wed Aug 22 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D9-1mdk
- 2.2.9
- used new source packaging policy
- added samples data

* Wed Aug 08 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.2.D6-1mdk
- first Mandrake release
