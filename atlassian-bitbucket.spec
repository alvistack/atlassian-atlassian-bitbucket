# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-bitbucket
Epoch: 100
Version: 7.21.5
Release: 4%{?dist}
Summary: Atlassian Bitbucket
License: Apache-2.0
URL: https://www.atlassian.com/software/bitbucket
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: chrpath
BuildRequires: fdupes
Requires(pre): shadow-utils
Requires: git
Requires: java

%description
Bitbucket Server is an on-premises source code management solution for
Git that's secure, fast, and enterprise grade. Create and manage
repositories, set up fine-grained permissions, and collaborate on code -
all with the flexibility of your servers.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/bitbucket
cp -rfT bitbucket %{buildroot}/opt/atlassian/bitbucket
install -Dpm644 -t %{buildroot}%{_unitdir} bitbucket.service
chmod a+x %{buildroot}/opt/atlassian/bitbucket/bin/start-bitbucket.sh
chmod a+x %{buildroot}/opt/atlassian/bitbucket/bin/stop-bitbucket.sh
find %{buildroot}/opt/atlassian/bitbucket -type f -name '*.so' -exec chrpath -d {} \;
find %{buildroot}/opt/atlassian/bitbucket -type f -name '*.bak' -delete
find %{buildroot}/opt/atlassian/bitbucket -type f -name '*.orig' -delete
find %{buildroot}/opt/atlassian/bitbucket -type f -name '*.rej' -delete
fdupes -qnrps %{buildroot}/opt/atlassian/bitbucket

%check

%pre
set -euxo pipefail

BITBUCKET_HOME=/var/atlassian/application-data/bitbucket

if [ ! -d $BITBUCKET_HOME -a ! -L $BITBUCKET_HOME ]; then
    mkdir -p $BITBUCKET_HOME
fi

if ! getent group bitbucket >/dev/null; then
    groupadd \
        --system \
        bitbucket
fi

if ! getent passwd bitbucket >/dev/null; then
    useradd \
        --system \
        --gid bitbucket \
        --home-dir $BITBUCKET_HOME \
        --no-create-home \
        --shell /usr/sbin/nologin \
        bitbucket
fi

chown -Rf bitbucket:bitbucket $BITBUCKET_HOME
chmod 0750 $BITBUCKET_HOME

%post
set -euxo pipefail

BITBUCKET_CATALINA=/opt/atlassian/bitbucket

chown -Rf bitbucket:bitbucket $BITBUCKET_CATALINA
chmod 0700 $BITBUCKET_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%{_unitdir}/bitbucket.service
/opt/atlassian/bitbucket

%changelog
