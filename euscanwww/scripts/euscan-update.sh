#!/bin/sh

## Update local trees
# emerge --sync
# layman -S

## Also update eix database, because we use eix internaly
# eix-update

## Scan portage (packages, versions)
# python manage.py scan-portage --all

## Scan metadata (herds, maintainers, homepages, ...)
# python manage.py scan-metadata --all

## Scan uptsream packages
# python manage.py scan-upstream --all
# python manage.py list-packages | gparallel --jobs 150% euscan | python manage.py scan-upstream --feed