from djeuscan.feeds import BaseFeed
from euscan_accounts.helpers import get_profile, get_account_versionlogs


class UserFeed(BaseFeed):
    link = "/"

    def description(self, data):
        return "%s - last euscan changes" % data["user"]

    def title(self, data):
        return "%s - watched packages" % data["user"]

    def get_object(self, request):
        return {
            "user": request.user,
            "options": request.GET,
        }

    def _items(self, data):
        user = data["user"]

        profile = get_profile(user)
        vlogs = get_account_versionlogs(profile)

        return vlogs, 100
