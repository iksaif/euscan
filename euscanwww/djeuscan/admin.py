from djeuscan.models import Package, Version, VersionLog, EuscanResult, \
    Log, WorldLog, CategoryLog, HerdLog, MaintainerLog, Herd, Maintainer
from django.contrib import admin


class EuscanResultAdmin(admin.ModelAdmin):
    search_fields = ('package__name', 'package__category')
    list_filter = ('datetime', )
    ordering = ["-datetime"]


class HerdAdmin(admin.ModelAdmin):
    search_fields = ('herd', 'email')
    ordering = ["herd"]


class MaintainerAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email')
    ordering = ["name"]


class PackageAdmin(admin.ModelAdmin):
    search_fields = ('category', 'name')
    list_filter = ('category', )


class VersionAdmin(admin.ModelAdmin):
    search_fields = ('package__name', 'package__category')
    list_filter = ('overlay', 'packaged', 'alive')


admin.site.register(Package, PackageAdmin)

admin.site.register(Herd, HerdAdmin)
admin.site.register(Maintainer, MaintainerAdmin)

admin.site.register(Version, VersionAdmin)
admin.site.register(VersionLog)

admin.site.register(EuscanResult, EuscanResultAdmin)

admin.site.register(Log)
admin.site.register(WorldLog)
admin.site.register(CategoryLog)
admin.site.register(HerdLog)
admin.site.register(MaintainerLog)
