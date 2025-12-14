from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Aegis",
    "SITE_HEADER": "Aegis",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Navigation",
                "separator": False,
                "collapsible": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index")
                    }
                ]
            },
            {
                "title": "User Management",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": reverse_lazy("admin:authentication_user_changelist")
                    },
                    {
                        "title": "Groups",
                        "icon": "groups",
                        "link": reverse_lazy("admin:authentication_groupproxy_changelist")
                    }
                ]
            },
            {
                "title": "Packages",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Packages",
                        "icon": "package",
                        "link": reverse_lazy("admin:packages_package_changelist")
                    },
                    {
                        "title": "Packages Version",
                        "icon": "deployed_code",
                        "link": reverse_lazy("admin:packages_packageversion_changelist")
                    },
                    {
                        "title": "Packages Version Files",
                        "icon": "files",
                        "link": reverse_lazy("admin:packages_packagefile_changelist")
                    }
                ]
            }
        ]
    }
}
