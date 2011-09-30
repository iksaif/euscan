#!/bin/sh

## Setup some vars to use local portage tree
# export PATH=${HOME}/euscan/:${PATH}
# export ROOT=${HOME}/local
# export PORTAGE_CONFIGROOT=${ROOT}
# export EIX_CACHEFILE=${HOME}/local/var/cache/eix

## Update local trees
# emerge --sync --root=${ROOT} --config-root=${PORTAGE_CONFIGROOT}
# ROOT="/" layman -S --config=${ROOT}/etc/layman/layman.cfg

## Generate ebuild cache to speed up eix
# cd ${ROOT}/var/lib/layman/ && \
# for overlay in **/; do
#     [ ! -f ${overlay}profiles/repo_name ] && continue
#
#    echo "egencache ${overlay}"
#    egencache --jobs=8 --rsync \
#        --repo=$(cat ${overlay}profiles/repo_name) \
#	--config-root=${PORTAGE_CONFIGROOT} \
#	--update --update-use-local-desc
# done

## Also update eix database, because we use eix internaly
# eix-update

## Go to euscanwww dir
# cd ${HOME}/euscan/euscanwww/

## Scan portage (packages, versions)
# python manage.py scan-portage --all --purge-versions --purge-packages
# eix --only-names -x | sort --random-sort | gparallel --eta --load 8 --jobs 400% --max-args=64 python manage.py scan-metadata

## Scan metadata (herds, maintainers, homepages, ...)
# python manage.py scan-metadata --all

## Scan uptsream packages
# python manage.py scan-upstream --all
# eix --only-names -x | gparallel --jobs 400% euscan | python manage.py scan-upstream --feed --purge-versions

## Update counters
# python manage.py update-counters
