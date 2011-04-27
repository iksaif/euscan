#!/bin/sh

## Setup some vars to use local portage tree
# export PATH=${HOME}/euscan/:${PATH}
# export PORTAGE_CONFIGROOT=${HOME}/local
# export ROOT=${HOME}/local
# export EIX_CACHEFILE=${HOME}/local/var/cache/eix

## Go to euscanwww dir
# cd ${HOME}/euscan/euscanwww/

## Update local trees
# emerge --sync --root=${ROOT} --config-root=${PORTAGE_CONFIGROOT}
# ROOT="/" layman -S --config=${ROOT}/etc/layman/layman.cfg

## Also update eix database, because we use eix internaly
# eix-update

## Scan portage (packages, versions)
# python manage.py scan-portage --all

## Scan metadata (herds, maintainers, homepages, ...)
# python manage.py scan-metadata --all

## Scan uptsream packages
# python manage.py scan-upstream --all
# eix --only-names -x | gparallel --jobs 400% euscan | python manage.py scan-upstream --feed
