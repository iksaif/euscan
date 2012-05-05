"""
djeuscan.managers
"""

from django.db import models
from djeuscan.helpers import xint, rename_fields, select_related_last_versions

def gen_n_function(field_name):
    def n_method(self):
        res = self.aggregate(models.Sum(field_name))[field_name + '__sum']
        return xint(res)
    n_method.func_name = field_name
    return n_method


N_LIST = ['n_packaged','n_overlay','n_versions']

ANNOTATE_DICT = { name: models.Sum(name) for name in N_LIST }

class PackageMixin(object):
     
    for name in N_LIST:
        locals()[name] = gen_n_function(name)
     
    def n_upstream(self):
        return self.n_versions() - self.n_packaged() - self.n_overlay()

    def categories(self):
        """
        Returns all the available categories
        """
        return self.values('category').annotate(**ANNOTATE_DICT)

    def herds(self, rename=False):
        """
        Returns all the available herds
        """
        # FIXME: optimize the query, it uses 'LEFT OUTER JOIN' instead of
        # 'INNER JOIN'
        res = self.filter(herds__isnull=False)
        res = res.values('herds__herd').annotate(**ANNOTATE_DICT)

        if rename:
            res = rename_fields(res, [('herds__herd', 'herd')])

        return res

    def maintainers(self, rename=False):
        """
        Returns all the available maintainers
        """
        res = self.filter(maintainers__isnull=False).values(
            'maintainers__id', 'maintainers__name', 'maintainers__email'
        )
        res = res.annotate(**ANNOTATE_DICT)

        if rename:
            res = rename_fields(
                res,
                [('maintainers__id', 'id'),
                ('maintainers__name', 'name'),
                ('maintainers__email', 'email')]
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

    def for_maintainer(self, maintainer, last_versions=False):
        """
        Returns packages that belong to the given maintainer
        """
        res = self.filter(maintainers__id=maintainer.id)

        if last_versions:
            select_related_last_versions(res)

        return res

    def for_herd(self, herd, last_versions=False):
        """
        Returns packages that belong to the given herd
        """
        res = self.filter(herds__id=herd.id)

        if last_versions:
            select_related_last_versions(res)

        return res

    def for_category(self, category, last_versions=False):
        """
        Returns packages that belong to the given category
        """
        res = self.filter(category=category)

        if last_versions:
            select_related_last_versions(res)

        return res


class PackageQuerySet(models.query.QuerySet, PackageMixin):
    pass


class PackageManager(models.Manager, PackageMixin):
    def get_query_set(self):
        return PackageQuerySet(self.model, using=self._db)
