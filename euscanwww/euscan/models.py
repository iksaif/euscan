from django.db import models
from datetime import datetime

class Herd(models.Model):
    herd = models.CharField(max_length=128, unique=True)
    email = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        if self.email:
            return '%s <%s>' % (self.herd, self.email)
        return self.herd

class Maintainer(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return '%s <%s>' % (self.name, self.email)

class Package(models.Model):
    category = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    homepage = models.CharField(max_length=256, blank=True)
    herds = models.ManyToManyField(Herd, blank=True)
    maintainers = models.ManyToManyField(Maintainer, blank=True)

    ' For performance, we keep pre-computed counters '
    n_versions = models.IntegerField(default=0)
    n_packaged = models.IntegerField(default=0)
    n_overlay = models.IntegerField(default=0)

    ' And we also pre-compute last versions '
    last_version_gentoo = models.ForeignKey('Version', blank=True, null=True,
                                            related_name="last_version_gentoo")
    last_version_overlay = models.ForeignKey('Version', blank=True, null=True,
                                             related_name="last_version_overlay")
    last_version_upstream = models.ForeignKey('Version', blank=True, null=True,
                                              related_name="last_version_upstream")

    def __unicode__(self):
        return '%s/%s' % (self.category, self.name)

    class Meta:
        unique_together = ['category', 'name']

class Version(models.Model):
    package = models.ForeignKey(Package)
    slot = models.CharField(max_length=128)
    revision = models.CharField(max_length=128)
    version = models.CharField(max_length=128)
    packaged = models.BooleanField()
    overlay = models.CharField(max_length=128, default='gentoo', db_index=True)
    urls = models.TextField(blank=True)
    alive = models.BooleanField(default=True, db_index=True)

    def __unicode__(self):
        return '%s/%s-%s-%s:%s [%s]' % (self.package.category, self.package.name,
                                        self.version, self.revision, self.slot,
                                        self.overlay)

    class Meta:
        unique_together = ['package', 'slot', 'revision', 'version', 'overlay']

class VersionLog(models.Model):
    VERSION_ADDED = 1
    VERSION_REMOVED = 2
    VERSION_ACTIONS = (
        (VERSION_ADDED, 'Added'),
        (VERSION_REMOVED, 'Removed')
    )

    package = models.ForeignKey(Package)
    datetime = models.DateTimeField(default=datetime.now())
    slot = models.CharField(max_length=128)
    revision = models.CharField(max_length=128)
    version = models.CharField(max_length=128)
    packaged = models.BooleanField()
    overlay = models.CharField(max_length=128, default='gentoo')
    action = models.IntegerField(choices=VERSION_ACTIONS)

    def tag(self):
        return '%s-%s:%s-[%s]' % (self.version, self.revision, self.slot,
                                  self.overlay)

    def __unicode__(self):
        txt = '+ ' if self.action == self.VERSION_ADDED else '- '
        txt += '%s/%s-%s-%s:%s [%s]' % (self.package.category, self.package.name,
                                        self.version, self.revision, self.slot,
                                        self.overlay if self.overlay else '<upstream>')
        return txt

class EuscanResult(models.Model):
    package = models.ForeignKey(Package)
    datetime = models.DateTimeField()
    result = models.TextField(blank=True)

# Keep data for charts
class Log(models.Model):
    datetime = models.DateTimeField()

    ' Packages up to date in the main portage tree '
    n_packages_gentoo   = models.IntegerField(default=0)
    ' Packages up to date in an overlay '
    n_packages_overlay  = models.IntegerField(default=0)
    ' Packages outdated '
    n_packages_outdated = models.IntegerField(default=0)

    ' Versions in the main portage tree '
    n_versions_gentoo   = models.IntegerField(default=0)
    ' Versions in overlays '
    n_versions_overlay  = models.IntegerField(default=0)
    ' Upstream versions, not in the main tree or overlays '
    n_versions_upstream = models.IntegerField(default=0)

    def __unicode__(self):
        return u'[%d:%d:%d] [%d:%d:%d]' % \
            (self.n_packages_gentoo, self.n_packages_overlay, self.n_packages_outdated, \
                 self.n_versions_gentoo, self.n_versions_overlay, self.n_versions_upstream)

class WorldLog(Log):
    def __unicode__(self):
        return u'world ' + Log.__unicode__(self)

class CategoryLog(Log):
    category = models.CharField(max_length=128)

    def __unicode__(self):
        return u'%s %s' % (self.category, Log.__unicode__(self))

class HerdLog(Log):
    herd = models.ForeignKey(Herd)

    def __unicode__(self):
        return u'%s %s' % (self.herd, Log.__unicode__(self))

class MaintainerLog(Log):
    maintainer = models.ForeignKey(Maintainer)

    def __unicode__(self):
        return u'%s %s' % (self.maintainer, Log.__unicode__(self))

