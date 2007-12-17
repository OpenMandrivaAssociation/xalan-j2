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

%define section free
%define cvs_version 2_7_0
%define gcj_support 0

Name:           xalan-j2
Version:        2.7.0
Release:        %mkrel 2.8
Epoch:          0
Summary:        Java XSLT processor
License:        Apache Software License
Source0:        http://www.apache.org/dist/xml/xalan-j/xalan-j_2_7_0-src.tar.bz2
Patch0:         %{name}-noxsltcdeps.patch
Patch1:         %{name}-manifest.patch
Patch2:         %{name}-crosslink.patch
URL:            http://xalan.apache.org/
Group:          Development/Java
#Vendor:         JPackage Project
#Distribution:   JPackage
%if %{gcj_support}
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
BuildRequires: java-gcj-compat-devel
%else
BuildArch:      noarch
%endif
Provides:       jaxp_transform_impl
Requires:       jaxp_parser_impl
Requires:	update-alternatives
Requires:	xerces-j2 >= 0:2.7.1
Requires:	xml-commons-jaxp-1.3-apis >= 0:1.3.03
BuildRequires:  java-rpmbuild >= 0:1.6
BuildRequires:	java-devel
BuildRequires:  ant
BuildRequires:  bcel
BuildRequires:	jlex
BuildRequires:	java_cup
BuildRequires:	regexp
BuildRequires:	sed
BuildRequires:  xerces-j2 >= 0:2.7.1
BuildRequires:  xml-commons-jaxp-1.3-apis >= 0:1.3.03

%description
Xalan is an XSLT processor for transforming XML documents into HTML,
text, or other XML document types. It implements the W3C Recommendations
for XSL Transformations (XSLT) and the XML Path Language (XPath). It can
be used from the command line, in an applet or a servlet, or as a module
in other program.

%package        xsltc
Summary:        XSLT compiler
Group:          Development/Java
Requires:	bcel
Requires:       java_cup
Requires:	jaxp_parser_impl
Requires:	jlex
Requires:	regexp

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
BuildRequires:  java-javadoc

%description    javadoc
Javadoc for %{name}.

%package        demo
Summary:        Demo for %{name}
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       servletapi5
BuildRequires:  servletapi5

%description    demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n xalan-j_%{cvs_version}
%patch0 -p0
#%patch1 -p0
#%patch2 -p0
# Remove all binary libs, except ones needed to build docs and N/A elsewhere.
for j in $(find . -name "*.jar"); do
	rm -f $j
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

%ant \
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


%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 build/xalan-interpretive.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -p -m 644 build/xsltc.jar \
  $RPM_BUILD_ROOT%{_javadir}/xsltc-%{version}.jar
install -p -m 644 build/serializer.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-serializer-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

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

# jaxp_transform_impl ghost symlink
ln -s %{_sysconfdir}/alternatives \
  $RPM_BUILD_ROOT%{_javadir}/jaxp_transform_impl.jar

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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

%if %{gcj_support}
%postun xsltc
%{clean_gcjdb}
%endif

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%if %{gcj_support}
%post demo
%{update_gcjdb}

%postun demo
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc KEYS licenses/xalan.LICENSE.txt licenses/xalan.NOTICE.txt licenses/serializer.LICENSE.txt licenses/serializer.NOTICE.txt
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-serializer-%{version}.jar
%{_javadir}/%{name}-serializer.jar
%ghost %{_javadir}/jaxp_transform_impl.jar
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

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
%ghost %doc %{_javadocdir}/%{name}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}


