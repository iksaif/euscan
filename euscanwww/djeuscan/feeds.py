from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse

from djeuscan.models import Package, Herd, Maintainer, VersionLog


class BaseFeed(Feed):
    feed_type = Atom1Feed
    author_name = 'euscan'
    item_author_name = author_name
    ttl = 3600

    def item_title(self, vlog):
        return str(vlog)

    def item_description(self, vlog):
        if vlog.overlay:
            txt = 'Version %s-%s [%s] of package %s ' % \
                (vlog.version, vlog.revision, vlog.slot, vlog.package)
        else:
            txt = 'Version %s of package %s ' % (vlog.version, vlog.package)
        if vlog.action == vlog.VERSION_REMOVED:
            if not vlog.overlay:
                txt += 'has been removed upstream'
            else:
                txt += 'has been removed from overlay "%s"' % vlog.overlay
        if vlog.action == vlog.VERSION_ADDED:
            if not vlog.overlay:
                txt += 'has been added upstream'
            else:
                txt += 'has been added to overlay "%s"' % vlog.overlay

        return txt

    def item_link(self, vlog):
        kwargs = {'category': vlog.package.category,
                  'package': vlog.package.name}
        return "%s#%s" % (reverse('djeuscan.views.package', kwargs=kwargs),
                          vlog.tag())

    def item_pubdate(self, vlog):
        return vlog.datetime

    def item_categories(self, vlog):
        return [vlog.package.category]


class GlobalFeed(BaseFeed):
    title = "euscan"
    link = "/"
    description = "Last euscan changes"

    def categories(self):
        categories = Package.objects.values('category').distinct()
        return [category['category'] for category in categories]

    def items(self):
        return VersionLog.objects.order_by('-id')[:250]


class PackageFeed(BaseFeed):
    feed_type = Atom1Feed

    def get_object(self, request, category, package):
        return get_object_or_404(Package, category=category, name=package)

    def title(self, package):
        return "%s" % package

    def link(self, package):
        return reverse('djeuscan.views.package', args=[package.category,
                       package.name])

    def description(self, package):
        return package.description

    def items(self, package):
        return VersionLog.objects.filter(package=package).order_by('-id')[:30]

    def item_description(self, vlog):
        return ''


class MaintainerFeed(BaseFeed):
    feed_type = Atom1Feed

    def get_object(self, request, maintainer_id):
        return get_object_or_404(Maintainer, id=maintainer_id)

    def title(self, maintainer):
        return "%s" % maintainer

    def description(self, maintainer):
        return "Last changes for %s" % maintainer

    def link(self, maintainer):
        return reverse('djeuscan.views.maintainer',
                       kwargs={'maintainer_id': maintainer.id})

    def items(self, maintainer):
        q = VersionLog.objects.filter(package__maintainers__id=maintainer.id)
        return q.order_by('-id')[:50]


class HerdFeed(BaseFeed):
    feed_type = Atom1Feed

    def get_object(self, request, herd):
        return get_object_or_404(Herd, herd=herd)

    def title(self, herd):
        return "%s" % herd

    def description(self, herd):
        return "Last changes for %s" % herd

    def link(self, herd):
        return reverse('djeuscan.views.herd', kwargs={'herd': herd.herd})

    def items(self, herd):
        q = VersionLog.objects.filter(package__herds__id=herd.id)
        return q.order_by('-id')[:100]


class CategoryFeed(BaseFeed):
    feed_type = Atom1Feed

    def get_object(self, request, category):
        if not Package.objects.filter(category=category).count():
            raise FeedDoesNotExist
        return category

    def title(self, category):
        return "%s" % category

    def description(self, category):
        return "Last changes for %s" % category

    def link(self, category):
        return reverse('djeuscan.views.category', args=[category])

    def items(self, category):
        q = VersionLog.objects.filter(package__category=category)
        return q.order_by('-id')[:100]
