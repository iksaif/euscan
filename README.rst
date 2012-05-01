What is euscan ?
================

dev-portage/euscan
------------------

euscan is available in portage as a dev package (app-portage/euscan-9999).
This tool allows to check if a given package/ebuild has new upstream versions
or not. It will use different heuristic to scan upstream and grab new versions
and related urls.

This tool was designed to mimic debian's uscan, but there is a major
difference between the two: uscan uses a specific "watch" file that describes
how it should scan packages, while euscan uses only what can already be found
in ebuilds. Of course, we could later add some informations in metadata.xml
to help euscan do its job more efficiently.

euscan heuristics are described in the "How does-it works ?" section.

### Examples

$ euscan amatch

 * dev-ruby/amatch-0.2.7 [gentoo]

Ebuild: /home/euscan/local/usr/portage/dev-ruby/amatch/amatch-0.2.7.ebuild
Repository: gentoo
Homepage: http://flori.github.com/amatch/
Description: Approximate Matching Extension for Ruby

 * SRC_URI is 'mirror://rubygems/amatch-0.2.7.gem'
 * Using: http://rubygems.org/api/v1/versions/amatch.json

Upstream Version: 0.2.8 http://rubygems.org/gems/amatch-0.2.8.gem

$ euscan rsyslog

 * app-admin/rsyslog-5.8.5 [gentoo]

Ebuild: /home/euscan/local/usr/portage/app-admin/rsyslog/rsyslog-5.8.5.ebuild
Repository: gentoo
Homepage: http://www.rsyslog.com/
Description: An enhanced multi-threaded syslogd with database support and more.

 * SRC_URI is 'http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.5.tar.gz'
 * Scanning: http://www.rsyslog.com/files/download/rsyslog/rsyslog-${PV}.tar.gz
 * Scanning: http://www.rsyslog.com/files/download/rsyslog
 * Generating version from 5.8.5
 * Brute forcing: http://www.rsyslog.com/files/download/rsyslog/rsyslog-${PV}.tar.gz
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.6.tar.gz ...        [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.7.tar.gz ...        [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.8.tar.gz ...        [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.0.tar.gz ...        [ ok ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.10.0.tar.gz ...         [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.11.0.tar.gz ...         [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.1.tar.gz ...        [ ok ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.2.tar.gz ...        [ ok ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.3.tar.gz ...        [ ok ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.12.0.tar.gz ...         [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.4.tar.gz ...        [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.5.tar.gz ...        [ !! ]
 * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.6.tar.gz ...        [ !! ]

Upstream Version: 5.9.1 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.1.tar.gz
Upstream Version: 5.9.0 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.0.tar.gz
Upstream Version: 5.9.3 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.3.tar.gz
Upstream Version: 5.9.2 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.2.tar.gz

### Hidden settings

You can configure some settings using the command line, but the __init__.py
file of the euscan package contains more settings, including blacklists and
default settings.

Maybe we should add the ability to use /etc/euscan.conf and
~/.config/euscan/euscan.conf to override these settings.

euscan-www: euscan as a service
-------------------------------

euscan-www is a web application that aggregates euscan results. For example
there is an instance of euscan-www that monitors gentoo-x86 + some official
overlays currently hosted at http://euscan.iksaif.net/ .

euscan-www uses django and provides some custom commands to feed the database.
You can use euscan-www on you system tree, or preferably you can use a local
tree to avoid messing with your system.

### Installation

Install requirements from PyPI using

  $ python setup.py develop

Extra dependencies:

  * portage python api
  * rrdtool[python]

Like any django web app, just start by editing settings.py and then run
these two commands.

  $ python manage.py syncdb
  $ python manage.py migrate

Now your instance is ready, you can just run this command to browse it.
If you want to host it publicly you should use a real webserver.

  $ python manage.py runserver

### Creating a local tree (optional)

Create a local tree with all that portage (and layman would need).
There is an example in euscanwww/scripts/local-tree/. See escan-update.sh
to know what env variables you need to run any portage related command in
this local tree.

### Scanning process

The scanning process is done by euscan-update.sh. You should read carefully
this script, and adapt it to your needs. For example it uses gparallel to
launch multiple process at a time, and you should adapt that to your number
of cpu and network bandwith.

Once your euscan-update.sh is ok, just run it.

  $ sh euscan-update.sh

### Custom Django management commands

euscan-www povides some new management commands, here is a short description
of these commands. Use "help" or read euscan-update.sh to get more informations.

#### list-packages

List packages stored in database.

#### scan-portage

Scan the portage tree and store new packages and versions in the database.

#### scan-metadata.py

Scan metadata and looks for homepage, maintainers and herds.

#### scan-upstream

Scan upstream package. The prefered way to use this script it to first launch
euscan on some packages, store the result of the file, and feed this command with
the result.

#### update-counters

Update statistics and rrd files.

#### regen-rrds

If you deleted your rrd files, this script will use the database to
regen them.

How does it work ?
==================

euscan has different heuristics to scan upstream and provides multiple
"handlers". First, here is a description of the generic handler.

Scanning directories
--------------------

The first thing to do is to scan directories. It's also what uscan do, but it
uses a file that describe what url and regexp to use to match packages.

euscan uses SRC_URI and tries to find the current version (or part of this version)
in the resolved SRC_URI and generate a regexp from that.

For example for app-accessibility/dash-4.10.1, SRC_URI is:
  mirror://gnome/sources/dasher/4.10/dasher-4.10.1.tar.bz2
euscan will scan pages based on this template:
  http://ftp.gnome.org/pub/gnome/sources/dasher/${0}.${1}/dasher-${PV}.tar.bz2

Then, from that, it will scan the top-most directory that doesn't depend on
the version, and try to go deeper from here.

Brute force
-----------

Like when scanning directories, a template of SRC_URI is built. Then euscan
generate next possible version numbers, and tries to download the url generated
from the template and the new version number.

For example, running euscan on portage/app-accessibility/festival-freebsoft-utils-0.6:
SRC_URI is 'http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-0.6.tar.gz'
Template is http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-${PV}.tar.gz
Generate version from 0.6: 0.7, 0.8, 0.10, ...
Try new urls: http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-0.7.tar.gz, etc..

Blacklists
----------

euscan uses blacklist for multiple purposes.

### BLACKLIST_VERSIONS

For versions that should not be checked at all. sys-libs/libstdc++-v3-3.4
is good example because it's a package which version will always be 3.4
(Compatibility package for running binaries linked against a pre gcc 3.4 libstdc++).


### BLACKLIST_PACKAGES

Some packages are dead, but SRC_URI refers to sources that are still being
updated, for example: sys-kernel/xbox-sources that uses the same sources as
vanilla-sources but is not updated the same way.

### SCANDIR_BLACKLIST_URLS

For urls that are not browsable. mirror://gentoo/ is a good example: it's
both stupid to scan it and very long/expensive.

### BRUTEFORCE_BLACKLIST_PACKAGES and BRUTEFORCE_BLACKLIST_URLS

Disable brute force on those packages and urls. Most of the time it's because
upstream is broken and will answer HTTP 200 even if the file doesn't exist.

### ROBOTS_TXT_BLACKLIST_DOMAINS

Don't respect robots.txt for these domains (sourcefourge, berlios, github.com).

Site handlers
-------------

### Pecl/PEAR

A site handler that uses the Pecl/PEAR rest API
(http://pear.php.net/manual/en/core.rest.php).

### Rubygems

This one uses rubygems's json API
(http://guides.rubygems.org/rubygems-org-api/)

### Pypy

Uses pypy's XML rpc API.
