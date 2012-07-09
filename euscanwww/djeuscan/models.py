from django.db import models
from django.core.validators import RegexValidator, validate_email, URLValidator
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from djeuscan.managers import PackageManager, VersionLogManager, \
    EuscanResultManager


validate_category = RegexValidator("^(?:\w+?-\w+?)|virtual$")
validate_name = RegexValidator("^\S+?$")
validate_revision = RegexValidator("^r\d+?$")
validate_url = URLValidator()


class Herd(models.Model):
    """
    A herd is a collection of packages
    """

    herd = models.CharField(max_length=128, unique=True,
                            validators=[validate_name])
    email = models.CharField(max_length=128, blank=True, null=True,
                             validators=[validate_email])

    def __unicode__(self):
        if self.email:
            return '%s <%s>' % (self.herd, self.email)
        return self.herd

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Herd, self).save(*args, **kwargs)


class Maintainer(models.Model):
    """
    The person who maintains a package
    """

    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128, unique=True,
                             validators=[validate_email])

    def __unicode__(self):
        return '%s <%s>' % (self.name, self.email)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Maintainer, self).save(*args, **kwargs)


class Package(models.Model):
    """
    A portage package
    """

    category = models.CharField(max_length=128, validators=[validate_category])
    name = models.CharField(max_length=128, validators=[validate_name])
    description = models.TextField(blank=True)
    homepage = models.TextField(blank=True)
    herds = models.ManyToManyField(Herd, blank=True)
    maintainers = models.ManyToManyField(Maintainer, blank=True)

    # For performance, we keep pre-computed counters
    n_versions = models.IntegerField(default=0)
    n_packaged = models.IntegerField(default=0)
    n_overlay = models.IntegerField(default=0)

    # And we also pre-compute last versions
    last_version_gentoo = models.ForeignKey(
        'Version', blank=True, null=True, related_name="last_version_gentoo",
        on_delete=models.SET_NULL
    )
    last_version_overlay = models.ForeignKey(
        'Version', blank=True, null=True, related_name="last_version_overlay",
        on_delete=models.SET_NULL
    )
    last_version_upstream = models.ForeignKey(
        'Version', blank=True, null=True, related_name="last_version_upstream",
        on_delete=models.SET_NULL
    )

    objects = PackageManager()

    class Meta:
        unique_together = ['category', 'name']

    def __unicode__(self):
        return '%s/%s' % (self.category, self.name)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Clean urls, accept only real urls
        urls = []
        for url in self.homepages:
            try:
                validate_url(url)
            except ValidationError:
                pass
            else:
                urls.append(url)
        self.homepage = " ".join(urls)

        super(Package, self).save(*args, **kwargs)

    @property
    def homepages(self):
        return self.homepage.split(' ')


class Version(models.Model):
    """
    Version associated to a package
    """

    package = models.ForeignKey(Package)
    slot = models.CharField(max_length=128, blank=True, default="")
    revision = models.CharField(max_length=128)
    version = models.CharField(max_length=128)
    packaged = models.BooleanField()
    overlay = models.CharField(max_length=128, default='gentoo', db_index=True,
                               validators=[validate_name], blank=True)
    urls = models.TextField(blank=True)
    alive = models.BooleanField(default=True, db_index=True)

    version_type = models.CharField(max_length=128, blank=True)
    handler = models.CharField(max_length=128, blank=True)
    confidence = models.IntegerField(default=0)

    class Meta:
        unique_together = ['package', 'slot', 'revision', 'version', 'overlay']

    def __unicode__(self):
        return '%s/%s-%s-%s:%s [%s]' % (
            self.package.category, self.package.name, self.version,
            self.revision, self.slot, self.overlay or "<upstream>"
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Version, self).save(*args, **kwargs)


class VersionLog(models.Model):
    VERSION_ADDED = 1
    VERSION_REMOVED = 2
    VERSION_ACTIONS = (
        (VERSION_ADDED, 'Added'),
        (VERSION_REMOVED, 'Removed')
    )

    package = models.ForeignKey(Package)
    datetime = models.DateTimeField(auto_now_add=True)
    slot = models.CharField(max_length=128, blank=True, default="")
    revision = models.CharField(max_length=128)
    version = models.CharField(max_length=128)
    packaged = models.BooleanField()
    overlay = models.CharField(max_length=128, default='gentoo',
                               validators=[validate_name], blank=True)
    action = models.IntegerField(choices=VERSION_ACTIONS)

    objects = VersionLogManager()

    def __unicode__(self):
        txt = '+ ' if self.action == self.VERSION_ADDED else '- '
        txt += '%s/%s-%s-%s:%s [%s]' % (
            self.package.category, self.package.name, self.version,
            self.revision, self.slot,
            self.overlay or '<upstream>'
        )
        return txt

    def save(self, *args, **kwargs):
        self.full_clean()
        super(VersionLog, self).save(*args, **kwargs)

    def tag(self):
        return '%s-%s:%s-[%s]' % (self.version, self.revision, self.slot,
                                  self.overlay)


class EuscanResult(models.Model):
    package = models.ForeignKey(Package)
    datetime = models.DateTimeField()
    result = models.TextField(blank=True)

    scan_time = models.FloatField(null=True, blank=True)
    ebuild = models.CharField(blank=True, max_length=256)

    objects = EuscanResultManager()

    class Meta:
        get_latest_by = "datetime"

    def save(self, *args, **kwargs):
        self.full_clean()
        super(EuscanResult, self).save(*args, **kwargs)

    def __unicode__(self):
        return '[%s] %s/%s' % (
            self.datetime, self.package.category, self.package.name
        )


class Log(models.Model):
    """
    Model used for keeping data for charts
    """

    datetime = models.DateTimeField()

    # Packages up to date in the main portage tree
    n_packages_gentoo = models.IntegerField(default=0)

    # Packages up to date in an overlay
    n_packages_overlay = models.IntegerField(default=0)

    # Packages outdated
    n_packages_outdated = models.IntegerField(default=0)

    # Versions in the main portage tree
    n_versions_gentoo = models.IntegerField(default=0)

    # Versions in overlays
    n_versions_overlay = models.IntegerField(default=0)

    # Upstream versions, not in the main tree or overlays
    n_versions_upstream = models.IntegerField(default=0)

    def __unicode__(self):
        return u'[%d:%d:%d] [%d:%d:%d]' % (
            self.n_packages_gentoo, self.n_packages_overlay,
            self.n_packages_outdated, self.n_versions_gentoo,
            self.n_versions_overlay, self.n_versions_upstream
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Log, self).save(*args, **kwargs)


class WorldLog(Log):
    def __unicode__(self):
        return u'world ' + Log.__unicode__(self)


class CategoryLog(Log):
    category = models.CharField(max_length=128, validators=[validate_category])

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


class RefreshPackageQuery(models.Model):
    package = models.ForeignKey(Package)
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return u'[%d] %s' % (self.priority, self.package)


class HerdAssociation(models.Model):
    user = models.ForeignKey(User)
    herd = models.ForeignKey(Herd)

    class Meta:
        unique_together = ['user', 'herd']

    def __unicode__(self):
        return u'[%s] %s' % (self.user, self.herd)


class MaintainerAssociation(models.Model):
    user = models.ForeignKey(User)
    maintainer = models.ForeignKey(Maintainer)

    class Meta:
        unique_together = ['user', 'maintainer']

    def __unicode__(self):
        return u'[%s] %s' % (self.user, self.maintainer)


class PackageAssociation(models.Model):
    user = models.ForeignKey(User)
    package = models.ForeignKey(Package)

    class Meta:
        unique_together = ['user', 'package']

    def __unicode__(self):
        return u'[%s] %s' % (self.user, self.package)


class CategoryAssociation(models.Model):
    user = models.ForeignKey(User)
    category = models.CharField(max_length=128, validators=[validate_category])

    class Meta:
        unique_together = ['user', 'category']

    def __unicode__(self):
        return u'[%s] %s' % (self.user, self.category)


class ProblemReport(models.Model):
    package = models.ForeignKey(Package)
    version = models.ForeignKey(Version, null=True, blank=True)
    subject = models.CharField(max_length=128)
    message = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"[%s] %s" % (self.datetime, self.package)
