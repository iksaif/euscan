from euscan.models import Herd, Maintainer, Package, Version, VersionLog, EuscanResult, Log, \
    WorldLog, CategoryLog, HerdLog, MaintainerLog
from django.contrib import admin

admin.site.register(Herd)
admin.site.register(Maintainer)

class PackageAdmin(admin.ModelAdmin):
    search_fields = ('category', 'name')
admin.site.register(Package, PackageAdmin)

admin.site.register(Version)
admin.site.register(VersionLog)
admin.site.register(EuscanResult)

admin.site.register(Log)
admin.site.register(WorldLog)
admin.site.register(CategoryLog)
admin.site.register(HerdLog)
admin.site.register(MaintainerLog)
