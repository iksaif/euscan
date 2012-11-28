""" Views """

import inspect
from annoying.decorators import render_to, ajax_request

from portage.versions import catpkgsplit

from django.http import HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models

from djeuscan.helpers import version_key, packages_from_names, \
    get_maintainer_or_404, get_make_conf, get_layman_repos
from djeuscan.models import Version, Package, Herd, Maintainer, EuscanResult, \
    VersionLog, RefreshPackageQuery, ProblemReport, Category, Overlay
from djeuscan.forms import WorldForm, PackagesForm, ProblemReportForm
from djeuscan.tasks import admin_tasks
from djeuscan import charts

from euscan_accounts.helpers import get_profile


@render_to('euscan/index.html')
def index(request):
    context = {
        'n_packaged': Package.objects.n_packaged(),
        'n_overlay': Package.objects.n_overlay(),
        'n_versions': Package.objects.n_versions(),
        'n_upstream': Package.objects.n_upstream(),
        'n_packages': Package.objects.count(),
        'n_herds': Herd.objects.count(),
        'n_maintainers': Maintainer.objects.count(),
    }
    try:
        context['last_scan'] = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        context['last_scan'] = None

    return context


@render_to('euscan/logs.html')
def logs(request):
    return {}


@render_to('euscan/categories.html')
def categories(request):
    try:
        last_scan = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    return {'categories': Package.objects.categories(), 'last_scan': last_scan}


@render_to('euscan/category.html')
def category(request, category):
    packages = Package.objects.for_category(category, last_versions=True)

    if not packages:
        return HttpResponseNotFound()

    try:
        last_scan = \
            EuscanResult.objects.for_category(category).latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    favourited = False
    if request.user.is_authenticated():
        try:
            category = Category.objects.get(name=category)
            favourited = category in get_profile(request.user).categories.all()
        except Category.DoesNotExist:
            pass

    return {'category': category, 'packages': packages, 'last_scan': last_scan,
            'favourited': favourited}


@render_to('euscan/herds.html')
def herds(request):
    herds = Package.objects.herds()

    try:
        last_scan = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    return {'herds': herds, 'last_scan': last_scan}


@render_to('euscan/herd.html')
def herd(request, herd):
    herd = get_object_or_404(Herd, herd=herd)
    packages = Package.objects.for_herd(herd, last_versions=True)

    try:
        last_scan = EuscanResult.objects.for_herd(herd).latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    favourited = False
    if request.user.is_authenticated():
        if herd in get_profile(request.user).herds.all():
            favourited = True

    return {'herd': herd, 'packages': packages, "last_scan": last_scan,
            'favourited': favourited}


@render_to('euscan/maintainers.html')
def maintainers(request):
    maintainers = Package.objects.maintainers()

    try:
        last_scan = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    return {'maintainers': maintainers, 'last_scan': last_scan}


@render_to('euscan/maintainer.html')
def maintainer(request, maintainer_id=None, maintainer_email=None):
    maintainer = get_maintainer_or_404(maintainer_id, maintainer_email)
    packages = Package.objects.for_maintainer(maintainer, last_versions=True)

    try:
        last_scan = \
            EuscanResult.objects.for_maintainer(maintainer).latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    favourited = False
    if request.user.is_authenticated():
        if maintainer in get_profile(request.user).maintainers.all():
            favourited = True

    return {'maintainer': maintainer, 'packages': packages,
            'last_scan': last_scan, 'favourited': favourited}


@render_to('euscan/overlays.html')
def overlays(request):
    overlays = Package.objects.overlays()

    try:
        last_scan = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    return {'overlays': overlays, 'last_scan': last_scan}


@render_to('euscan/overlay.html')
def overlay(request, overlay):
    packages = Package.objects.for_overlay(overlay)
    if not packages:
        return HttpResponseNotFound()

    try:
        last_scan = EuscanResult.objects.latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    favourited = False
    if request.user.is_authenticated():
        try:
            overlay = Overlay.objects.get(name=overlay)
            favourited = overlay in get_profile(request.user).overlays.all()
        except Overlay.DoesNotExist:
            pass

    return {'overlay': overlay, 'packages': packages, 'last_scan': last_scan,
            'favourited': favourited}


@render_to('euscan/package.html')
def package(request, category, package):
    package = get_object_or_404(Package, category=category, name=package)
    packaged = Version.objects.filter(package=package, packaged=True)
    upstream = Version.objects.filter(package=package, packaged=False)

    packaged = sorted(packaged, key=version_key)
    upstream = sorted(upstream, key=version_key)

    log = EuscanResult.objects.filter(package=package).\
                               order_by('-datetime')[:1]
    log = log[0] if log else None
    vlog = VersionLog.objects.for_package(package, order=True)

    try:
        last_scan = EuscanResult.objects.for_package(package).latest().datetime
    except EuscanResult.DoesNotExist:
        last_scan = None

    favourited = False
    if request.user.is_authenticated():
        if package in get_profile(request.user).packages.all():
            favourited = True

    try:
        refresh_query = RefreshPackageQuery.objects.get(package=package)
    except RefreshPackageQuery.DoesNotExist:
        refresh_requested = False
        refresh_pos = None
    else:
        refresh_requested = request.user in refresh_query.users.all()
        refresh_pos = refresh_query.position

    return {
        'package': package,
        'packaged': packaged,
        'upstream': upstream,
        'vlog': vlog,
        'log': log,
        'msg': log.messages if log else "",
        'last_scan': last_scan,
        'favourited': favourited,
        'refresh_requested': refresh_requested,
        'refresh_pos': refresh_pos,
    }


def package_metadata(request, overlay, category, package):
    package = get_object_or_404(Package, category=category, name=package)

    versions = Version.objects.filter(package=package, overlay=overlay)
    if len(versions) == 0:
        return HttpResponseNotFound()

    # XXX: Kinda ugly, it assumes that every version with the same overlay
    #      has the same metadata path
    version = versions[0]

    content = ""
    if version.metadata_path:
        try:
            with open(version.metadata_path) as meta_file:
                content = meta_file.read()
        except IOError:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
    return HttpResponse(content, content_type="text/plain")


def package_version_ebuild(request, overlay, cpv):
    category, package, version, revision = catpkgsplit(cpv)
    pkg = get_object_or_404(Package, category=category, name=package)
    obj = get_object_or_404(Version, package=pkg, version=version,
                            revision=revision, overlay=overlay)

    if obj.ebuild_path:
        try:
            with open(obj.ebuild_path) as ebuild_file:
                content = ebuild_file.read()
        except IOError:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
    return HttpResponse(content, content_type="text/plain")


@login_required
@render_to('euscan/problem.html')
def problem(request, category, package):
    package = get_object_or_404(Package, category=category, name=package)
    packaged = Version.objects.filter(package=package, packaged=True)
    upstream = Version.objects.filter(package=package, packaged=False)

    log = EuscanResult.objects.filter(package=package).\
                               order_by('-datetime')[:1]
    log = log[0] if log else None

    thanks_for_reporting = False

    if request.method == "POST":
        form = ProblemReportForm(package, request.POST)
        if form.is_valid():
            ProblemReport(
                package=package,
                version=form.cleaned_data["version"],
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
            ).save()
            thanks_for_reporting = True
    else:
        form = ProblemReportForm(package)

    return {
        'form': form,
        'thanks_for_reporting': thanks_for_reporting,
        'package': package,
        'packaged': packaged,
        'upstream': upstream,
        'msg': log.messages if log else "",
    }


@render_to('euscan/world.html')
def world(request):
    world_form = WorldForm()
    packages_form = PackagesForm()

    return {
        'world_form': world_form,
        'packages_form': packages_form
    }


@render_to('euscan/world_scan.html')
def world_scan(request):
    if 'world' in request.FILES:
        data = request.FILES['world'].read()
    elif 'packages' in request.POST:
        data = request.POST['packages']
    else:
        data = ""

    packages = packages_from_names(data)
    packages_ids = [p.pk for p in packages]

    favourited = False
    if len(packages) > 0 and request.user.is_authenticated():
        profile = get_profile(request.user)
        if len(packages) == len(profile.packages.filter(id__in=packages_ids)):
            favourited = True

    return {
        'packages': packages,
        'packages_ids': packages_ids,
        'favourited': favourited
    }


@render_to("euscan/about.html")
def about(request):
    return {}


@render_to("euscan/api.html")
def api(request):
    return {}


@render_to("euscan/feeds.html")
def feeds(request):
    return {}


@render_to("euscan/config.html")
def config(request):
    from euscan import CONFIG, BLACKLIST_VERSIONS, BLACKLIST_PACKAGES, \
        SCANDIR_BLACKLIST_URLS, BRUTEFORCE_BLACKLIST_PACKAGES, \
        BRUTEFORCE_BLACKLIST_URLS, ROBOTS_TXT_BLACKLIST_DOMAINS
    euscan_config = {
        "CONFIG": CONFIG,
        "BLACKLIST_VERSIONS": BLACKLIST_VERSIONS,
        "BLACKLIST_PACKAGES": BLACKLIST_PACKAGES,
        "SCANDIR_BLACKLIST_URLS": SCANDIR_BLACKLIST_URLS,
        "BRUTEFORCE_BLACKLIST_PACKAGES": BRUTEFORCE_BLACKLIST_PACKAGES,
        "BRUTEFORCE_BLACKLIST_URLS": BRUTEFORCE_BLACKLIST_URLS,
        "ROBOTS_TXT_BLACKLIST_DOMAINS": ROBOTS_TXT_BLACKLIST_DOMAINS,
    }
    make_conf = get_make_conf()
    layman_repos = get_layman_repos()

    return {
        "euscan_config": euscan_config,
        "make_conf": make_conf,
        "layman_repos": layman_repos,
    }


@render_to("euscan/statistics.html")
def statistics(request):
    handlers = (
        Version.objects.values("handler")
               .filter(overlay="")
               .annotate(n=models.Count("handler"),
                         avg_conf=models.Avg("confidence"))
    )
    for i in xrange(len(handlers)):
        if not handlers[i]['handler']:
            handlers[i]['handler'] = "unknown"
    return {"handlers": handlers}


@render_to("euscan/statistics_handler.html")
def statistics_handler(request, handler):
    if handler == "unknown":
        handler = ""
    packages = Package.objects.for_handler(handler)
    return {"handler": handler, "packages": packages}


def chart(request, **kwargs):
    from django.views.static import serve

    chart = kwargs['chart'] if 'chart' in kwargs else None

    if 'maintainer_id' in kwargs or 'maintainer_email' in kwargs:
        kwargs['maintainer'] = get_maintainer_or_404(
            kwargs.get('maintainer_id'),
            kwargs.get('maintainer_email')
        )
    if 'herd' in kwargs:
        kwargs['herd'] = get_object_or_404(Herd, herd=kwargs['herd'])

    for kw in ('-small', '-weekly', '-monthly', '-yearly'):
        if chart.endswith(kw):
            if kw in ('-weekly', '-monthly', '-yearly'):
                kwargs['period'] = kw
            kwargs[kw] = True
            chart = chart[:-len(kw)]

    if chart == 'pie-packages':
        path = charts.pie_packages(**kwargs)
    elif chart == 'pie-versions':
        path = charts.pie_versions(**kwargs)
    elif chart == 'packages':
        path = charts.packages(**kwargs)
    elif chart == 'versions':
        path = charts.versions(**kwargs)
    else:
        return HttpResponseNotFound()

    return serve(request, path, document_root=charts.CHARTS_ROOT)


def chart_maintainer(request, **kwargs):
    return chart(request, **kwargs)


def chart_herd(request, **kwargs):
    return chart(request, **kwargs)


def chart_category(request, **kwargs):
    return chart(request, **kwargs)


@ajax_request
def registered_tasks(request):
    data = {}
    for task in admin_tasks:
        argspec = inspect.getargspec(task.run)
        data[task.name] = {
            "args": argspec.args,
            "defaults": argspec.defaults,
            "default_types": None
        }
        if argspec.defaults is not None:
            data[task.name].update({
                "defaults_types": [type(x).__name__ for x in argspec.defaults]
            })
    return {"tasks": data}


@login_required
@require_POST
@ajax_request
def refresh_package(request, category, package):
    pkg = get_object_or_404(Package, category=category, name=package)

    obj, created = RefreshPackageQuery.objects.get_or_create(package=pkg)

    if request.user in \
       RefreshPackageQuery.objects.get(package=pkg).users.all():
        return {"result": "failure"}

    obj.users.add(request.user)
    if not created:
        obj.priority += 1
        obj.save()
    if created:
        from djeuscan.tasks import consume_refresh_queue
        consume_refresh_queue.delay()
    if "nojs" in request.POST:
        return redirect(reverse("package", args=(category, package)))
    else:
        return {"result": "success", "position": obj.position}
