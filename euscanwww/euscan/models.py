from django.db import models

class Herd(models.Model):
    herd = models.CharField(max_length=128, unique=True)
    email = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        if self.email:
            return '%s <%s>' % (self.herd, self.email)
        return self.herd

class Maintainer(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128)

    def __unicode__(self):
        return '%s <%s>' % (self.name, self.email)

    class Meta:
        unique_together = ['name', 'email']

class Package(models.Model):
    category = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    homepage = models.CharField(max_length=256, blank=True)
    herds = models.ManyToManyField(Herd, blank=True)
    maintainers = models.ManyToManyField(Maintainer, blank=True)

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
    overlay = models.CharField(max_length=128)
    urls = models.TextField(blank=True)

    def __unicode__(self):
        return '%s/%s-%s-%s:%s [%s]' % (self.package.category, self.package.name,
                                        self.version, self.revision, self.slot,
                                        self.overlay)

    class Meta:
        unique_together = ['package', 'slot', 'revision', 'version', 'overlay']

class EuscanResult(models.Model):
    package = models.ForeignKey(Package)
    startdate = models.DateTimeField()
    endstate = models.DateTimeField()
    result = models.TextField(blank=True)
