%global cvs_version 2_7_1

Name:           xalan-j2
Version:        2.7.1
Release:        22
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
Patch2:		https://src.fedoraproject.org/rpms/xalan-j2/raw/master/f/xalan-j2-CVE-2014-0107.patch
Patch3:		xalan-j-2.7.1-java-11.patch
URL:            http://xalan.apache.org/


BuildArch:      noarch
Provides:       jaxp_transform_impl
Requires:       xerces-j2
Requires(post): chkconfig
Requires(preun): chkconfig
BuildRequires:  java-devel
BuildRequires:	javapackages-local
BuildRequires:  ant
BuildRequires:  bcel
BuildRequires:  java_cup
BuildRequires:  regexp
BuildRequires:  sed
BuildRequires:  tomcat-servlet-3.0-api
BuildRequires:  xerces-j2 >= 2.7.1
BuildRequires:  xml-commons-apis >= 1.3
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

Requires:       %{name} = %{EVRD}
Requires:       tomcat-servlet-3.0-api

%description    demo
Demonstrations and samples for %{name}.

%prep
%autosetup -p1 -n xalan-j_%{cvs_version}
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

%mvn_file :xalan %{name} jaxp_transform_impl
%mvn_file :serializer %{name}-serializer
%mvn_file :xsltc xsltc
%mvn_package :xsltc xsltc

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
export CLASSPATH=$(build-classpath tomcat-servlet-api)

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

#mvn_artifact %{SOURCE2} build/xalan-interpretive.jar
#mvn_artifact %{SOURCE3} build/serializer.jar
#mvn_artifact %{SOURCE4} build/xsltc.jar

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

# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m 644 build/xalansamples.jar \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-samples.jar
install -p -m 644 build/xalanservlet.war \
  $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-servlet.war
cp -pr samples $RPM_BUILD_ROOT%{_datadir}/%{name}

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

%files demo
%{_datadir}/%{name}
