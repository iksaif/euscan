"""
djeuscan.managers
"""

from django.db import models
from djeuscan.helpers import xint


class PackageMixin(object):

    def n_packaged(self):
        res = self.aggregate(models.Sum('n_packaged'))['n_packaged__sum']
        return xint(res)

    def n_overlay(self):
        res = self.aggregate(models.Sum('n_overlay'))['n_overlay__sum']
        return xint(res)

    def n_versions(self):
        res = self.aggregate(models.Sum('n_versions'))['n_versions__sum']
        return xint(res)

    def n_upstream(self):
        return self.n_versions() - self.n_packaged() - self.n_overlay()

    def categories(self):
        """
        Returns all the available categories
        """
        return self.values('category').annotate(
            n_packaged=models.Sum('n_packaged'),
            n_overlay=models.Sum('n_overlay'),
            n_versions=models.Sum('n_versions')
        )

    def herds(self):
        """
        Returns all the available herds
        """
        # FIXME: optimize the query, it uses 'LEFT OUTER JOIN' instead of
        # 'INNER JOIN'
        res = self.filter(herds__isnull=False)
        res = res.values('herds__herd').annotate(
            n_packaged=models.Sum('n_packaged'),
            n_overlay=models.Sum('n_overlay'),
            n_versions=models.Sum('n_versions')
        )
        return res

    def maintainers(self):
        """
        Returns all the available maintainers
        """
        res = self.filter(maintainers__isnull=False).values(
            'maintainers__id', 'maintainers__name', 'maintainers__email'
        )
        res = res.annotate(
            n_packaged=models.Sum('n_packaged'),
            n_overlay=models.Sum('n_overlay'),
            n_versions=models.Sum('n_versions')
        )
        return res

    def overlays(self):
        """
        Returns the all available overlays
        """
        res = self.values('version__overlay').exclude(version__overlay='')
        return res.distinct()

    def for_overlay(self, overlay):
        """
        Returns packages that belong to the given overlay
        """
        packages = self.values(
            'id', 'name', 'category', 'n_versions', 'n_packaged', 'n_overlay'
        )
        return packages.filter(version__overlay=overlay).distinct()

    def for_maintainer(self, maintainer):
        """
        Returns packages that belong to the given maintainer
        """
        res = self.filter(maintainers__id=maintainer.id)

        # performance boost
        res = res.select_related(
            'last_version_gentoo',
            'last_version_overlay',
            'last_version_upstream'
        )

        return res

    def for_herd(self, herd):
        """
        Returns packages that belong to the given herd
        """
        res = self.filter(herds__id=herd.id)

        # performance boost
        res = res.select_related(
            'last_version_gentoo',
            'last_version_overlay',
            'last_version_upstream'
        )

        return res

    def for_category(self, category):
        """
        Returns packages that belong to the given category
        """
        res = self.filter(category=category)

        # performance boost
        res = res.select_related(
            'last_version_gentoo',
            'last_version_overlay',
            'last_version_upstream'
        )

        return res


class PackageQuerySet(models.query.QuerySet, PackageMixin):
    pass


class PackageManager(models.Manager, PackageMixin):
    def get_query_set(self):
        return PackageQuerySet(self.model, using=self._db)
