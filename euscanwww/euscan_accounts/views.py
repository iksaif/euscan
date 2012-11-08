from annoying.decorators import render_to, ajax_request

from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from djeuscan.models import Package, Category, Herd, Overlay
from djeuscan.helpers import get_maintainer_or_404

from euscan_accounts.feeds import UserFeed
from euscan_accounts.forms import PreferencesForm
from euscan_accounts.helpers import get_user_fav_infos, get_profile, \
    get_account_categories, get_account_herds, get_account_maintainers


@login_required
@render_to('euscan/accounts/index.html')
def accounts_index(request):
    user = request.user

    infos = get_user_fav_infos(user)
    infos['vlog'] = UserFeed().items({'user': user, 'options': {}})

    return infos


@login_required
@render_to('euscan/accounts/preferences.html')
def accounts_preferences(request):
    user = request.user
    prof = get_profile(user)

    updated = False
    if request.method == "POST":
        form = PreferencesForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save(force_update=True)

            prof.feed_upstream_info = form.cleaned_data["feed_upstream_info"]
            prof.feed_portage_info = form.cleaned_data["feed_portage_info"]
            prof.feed_show_adds = form.cleaned_data["feed_show_adds"]
            prof.feed_show_removals = form.cleaned_data["feed_show_removals"]
            prof.feed_ignore_pre = form.cleaned_data["feed_ignore_pre"]
            prof.feed_ignore_pre_if_stable = \
                form.cleaned_data["feed_ignore_pre_if_stable"]

            prof.email_activated = form.cleaned_data["email_activated"]
            prof.email_every = form.cleaned_data["email_every"]
            prof.email_ignore_pre = form.cleaned_data["email_ignore_pre"]
            prof.email_ignore_pre_if_stable = \
                form.cleaned_data["email_ignore_pre_if_stable"]

            prof.save(force_update=True)

            updated = True
    else:
        initial_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "feed_upstream_info": prof.feed_upstream_info,
            "feed_portage_info": prof.feed_portage_info,
            "feed_show_adds": prof.feed_show_adds,
            "feed_show_removals": prof.feed_show_removals,
            "feed_ignore_pre": prof.feed_ignore_pre,
            "feed_ignore_pre_if_stable": prof.feed_ignore_pre_if_stable,
            "email_activated": prof.email_activated,
            "email_every": prof.email_every,
            "email_ignore_pre": prof.email_ignore_pre,
            "email_ignore_pre_if_stable": prof.email_ignore_pre_if_stable,
        }
        form = PreferencesForm(initial_data)
    return {"form": form, "updated": updated}


@login_required
@render_to('euscan/accounts/categories.html')
def accounts_categories(request):
    return {"categories": get_account_categories(request.user)}


@login_required
@render_to('euscan/accounts/herds.html')
def accounts_herds(request):
    return {"herds": get_account_herds(request.user)}


@login_required
@render_to('euscan/accounts/maintainers.html')
def accounts_maintainers(request):
    return {"maintainers": get_account_maintainers(request.user)}


@login_required
@render_to('euscan/accounts/packages.html')
def accounts_packages(request):
    return {"packages": get_profile(request.user).packages.all()}


@login_required
@render_to('euscan/accounts/overlays.html')
def accounts_overlays(request):
    overlays = [obj.name for obj in get_profile(request.user).overlays.all()]
    return {"overlays": overlays}


@login_required
@require_POST
@ajax_request
def favourite_package(request, category, package):
    obj = get_object_or_404(Package, category=category, name=package)
    get_profile(request.user).packages.add(obj)
    if "nojs" in request.POST:
        return redirect(reverse("package", args=(category, package)))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_package(request, category, package):
    obj = get_object_or_404(Package, category=category, name=package)
    get_profile(request.user).packages.remove(obj)
    if "nojs" in request.POST:
        return redirect(reverse("package", args=(category, package)))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def favourite_herd(request, herd):
    obj = get_object_or_404(Herd, herd=herd)
    get_profile(request.user).herds.add(obj)
    if "nojs" in request.POST:
        return redirect(reverse("herd", args=(herd, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_herd(request, herd):
    obj = get_object_or_404(Herd, herd=herd)
    get_profile(request.user).herds.remove(obj)
    if "nojs" in request.POST:
        return redirect(reverse("herd", args=(herd, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def favourite_maintainer(request, maintainer_id=None, maintainer_email=None):
    obj = get_maintainer_or_404(maintainer_id, maintainer_email)
    get_profile(request.user).maintainers.add(obj)
    if "nojs" in request.POST:
        return redirect(reverse("maintainer", args=(obj.email, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_maintainer(request, maintainer_id=None, maintainer_email=None):
    obj = get_maintainer_or_404(maintainer_id, maintainer_email)
    get_profile(request.user).maintainers.remove(obj)
    if "nojs" in request.POST:
        return redirect(reverse("maintainer", args=(obj.email, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def favourite_category(request, category):
    obj = Category.objects.get(name=category)
    get_profile(request.user).categories.add(obj)
    if "nojs" in request.POST:
        return redirect(reverse("category", args=(category, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_category(request, category):
    obj = Category.objects.get(name=category)
    get_profile(request.user).categories.remove(obj)
    if "nojs" in request.POST:
        return redirect(reverse("category", args=(category, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def favourite_overlay(request, overlay):
    obj = Overlay.objects.get(name=overlay)
    get_profile(request.user).overlays.add(obj)
    if "nojs" in request.POST:
        return redirect(reverse("overlay", args=(overlay, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_overlay(request, overlay):
    obj = Overlay.objects.get(name=overlay)
    get_profile(request.user).overlays.remove(obj)
    if "nojs" in request.POST:
        return redirect(reverse("overlay", args=(overlay, )))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def favourite_world(request):
    if not "packages[]" in request.POST:
        return {"success": False}
    packages = request.POST.getlist("packages[]")
    objs = Package.objects.filter(id__in=packages)
    get_profile(request.user).packages.add(*objs)
    if "nojs" in request.POST:
        return redirect(reverse("world"))
    return {"success": True}


@login_required
@require_POST
@ajax_request
def unfavourite_world(request):
    if not "packages[]" in request.POST:
        return {"success": False}
    packages = request.POST.getlist("packages[]")
    objs = Package.objects.filter(id__in=packages)
    get_profile(request.user).packages.remove(*objs)
    if "nojs" in request.POST:
        return redirect(reverse("world"))
    return {"success": True}
