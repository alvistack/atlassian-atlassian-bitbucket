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
Version: 8.5.1
Release: 1%{?dist}
Summary: Atlassian Bitbucket
License: Apache-2.0
URL: https://www.atlassian.com/software/bitbucket
Source0: %{name}_%{version}.orig.tar.gz
Requires(pre): shadow-utils
BuildRequires: -post-build-checks
Requires(pre): chrpath
Requires(pre): fdupes
Requires(pre): patch
Requires(pre): wget
Requires: git

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
install -Dpm644 -t %{buildroot}%{_unitdir} bitbucket.service
install -Dpm644 -t %{buildroot}/opt/atlassian/bitbucket atlassian-bitbucket.patch

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

BITBUCKET_DOWNLOAD_URL=http://product-downloads.atlassian.com/software/stash/downloads/atlassian-bitbucket-8.5.1.tar.gz
BITBUCKET_DOWNLOAD_DEST=/tmp/atlassian-bitbucket-8.5.1.tar.gz
BITBUCKET_DOWNLOAD_CHECKSUM=89f837628614efac21d6966a03db1bf03236286523cf0d5f9207507ae9c3d3da

BITBUCKET_CATALINA=/opt/atlassian/bitbucket

wget -c $BITBUCKET_DOWNLOAD_URL -O $BITBUCKET_DOWNLOAD_DEST
echo -n "$BITBUCKET_DOWNLOAD_CHECKSUM $BITBUCKET_DOWNLOAD_DEST" | sha256sum -c -

mkdir -p $BITBUCKET_CATALINA
find $BITBUCKET_CATALINA -mindepth 1 | grep -v atlassian-bitbucket.patch | xargs rm -rf || echo $?
tar zxf $BITBUCKET_DOWNLOAD_DEST -C $BITBUCKET_CATALINA --strip-components=1

cat $BITBUCKET_CATALINA/atlassian-bitbucket.patch | patch -p1
chmod a+x $BITBUCKET_CATALINA/bin/start-bitbucket.sh
chmod a+x $BITBUCKET_CATALINA/bin/stop-bitbucket.sh
find $BITBUCKET_CATALINA -type f -name '*.so' -exec chrpath -d {} \;
find $BITBUCKET_CATALINA -type f -name '*.bak' -delete
find $BITBUCKET_CATALINA -type f -name '*.orig' -delete
find $BITBUCKET_CATALINA -type f -name '*.rej' -delete
fdupes -qnrps $BITBUCKET_CATALINA

chown -Rf bitbucket:bitbucket $BITBUCKET_CATALINA
chmod 0700 $BITBUCKET_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%dir /opt/atlassian/bitbucket
%{_unitdir}/bitbucket.service
/opt/atlassian/bitbucket/atlassian-bitbucket.patch

%changelog
