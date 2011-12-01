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
Release:        5
Summary:        Java XSLT processor
# samples/servlet/ApplyXSLTException.java is ASL 1.1
# src/org/apache/xpath/domapi/XPathStylesheetDOM3Exception.java is W3C
License:        ASL 1.1 and ASL 2.0 and W3C
Source0:        http://www.apache.org/dist/xml/xalan-j/xalan-j_2_7_1-src.tar.gz
Source1:        %{name}-serializer-MANIFEST.MF
Patch0:         %{name}-noxsltcdeps.patch
Patch1:         %{name}-manifest.patch
Patch2:         %{name}-crosslink.patch
#This patch uses xalan-j2-serializer.jar in the MANIFEST files instead of serializer
Patch3:		%{name}-src-MANIFEST-MF.patch
URL:            http://xalan.apache.org/
Group:          Development/Java
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildArch:      noarch
Provides:       jaxp_transform_impl
Requires:       xerces-j2
Requires(post): chkconfig
Requires(preun): chkconfig
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:	java-devel
BuildRequires:  ant
BuildRequires:  bcel
BuildRequires:	jlex
BuildRequires:	java_cup
BuildRequires:	regexp
BuildRequires:	sed
BuildRequires:	servlet25
BuildRequires:  xerces-j2 >= 0:2.7.1
BuildRequires:  xml-commons-apis >= 0:1.3
BuildRequires:  xml-stylebook

%description
Xalan is an XSLT processor for transforming XML documents into HTML,
text, or other XML document types. It implements the W3C Recommendations
for XSL Transformations (XSLT) and the XML Path Language (XPath). It can
be used from the command line, in an applet or a servlet, or as a module
in other program.

%package        xsltc
Summary:        XSLT compiler
Group:          Development/Java
Requires:       java_cup
Requires:	bcel
Requires:	jlex
Requires:	regexp
Requires:	xerces-j2

%description    xsltc
The XSLT Compiler is a Java-based tool for compiling XSLT stylesheets into
lightweight and portable Java byte codes called translets.

%package        manual
Summary:        Manual for %{name}
Group:          Development/Java

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires:       jpackage-utils
BuildRequires:  java-javadoc

%description    javadoc
Javadoc for %{name}.

%package        demo
Summary:        Demo for %{name}
Group:          Development/Java
Requires:       %{name} = %{version}-%{release}, servlet25

%description    demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n xalan-j_%{cvs_version}
%patch0 -p0
#%patch3 -p0
#%patch1 -p0
#%patch2 -p0
# Remove all binary libs, except ones needed to build docs and N/A elsewhere.
for j in $(find . -name "*.jar"); do
	mv $j $j.no
done
# FIXME who knows where the sources are? xalan-j1 ?
mv tools/xalan2jdoc.jar.no tools/xalan2jdoc.jar
mv tools/xalan2jtaglet.jar.no tools/xalan2jtaglet.jar

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
ln -sf $(build-classpath jlex) JLex.jar
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
rm -rf %{buildroot}

# inject OSGi manifests
mkdir -p META-INF
cp -p %{SOURCE1} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u build/serializer.jar META-INF/MANIFEST.MF

# jars
install -d -m 755 %{buildroot}%{_javadir}
install -p -m 644 build/xalan-interpretive.jar \
  %{buildroot}%{_javadir}/%{name}.jar
install -p -m 644 build/xsltc.jar \
  %{buildroot}%{_javadir}/xsltc.jar
install -p -m 644 build/serializer.jar \
  %{buildroot}%{_javadir}/%{name}-serializer.jar

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -pr build/docs/apidocs/* %{buildroot}%{_javadocdir}/%{name}
rm -rf build/docs/apidocs

# demo
install -d -m 755 %{buildroot}%{_datadir}/%{name}
install -p -m 644 build/xalansamples.jar \
  %{buildroot}%{_datadir}/%{name}/%{name}-samples.jar
install -p -m 644 build/xalanservlet.war \
  %{buildroot}%{_datadir}/%{name}/%{name}-servlet.war
cp -pr samples %{buildroot}%{_datadir}/%{name}

# fix link between manual and javadoc
(cd build/docs; ln -sf %{_javadocdir}/%{name} apidocs)

# jaxp_transform_impl ghost symlink
ln -s %{_sysconfdir}/alternatives \
  %{buildroot}%{_javadir}/jaxp_transform_impl.jar


%clean
rm -rf %{buildroot}


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

%files
%defattr(-,root,root,-)
%doc KEYS LICENSE.txt NOTICE.txt readme.html
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-serializer.jar
%ghost %{_javadir}/jaxp_transform_impl.jar

%files xsltc
%defattr(-,root,root,-)
%{_javadir}/xsltc.jar

%files manual
%defattr(-,root,root,-)
%doc build/docs/*

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}

%files demo
%defattr(-,root,root,-)
%{_datadir}/%{name}

