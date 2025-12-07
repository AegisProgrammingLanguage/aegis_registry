from django.contrib import admin
from .models import Package, PackageVersion


class PackageVersionInline(admin.TabularInline):
    model = PackageVersion
    extra = 0


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "description", "created_at"]
    inlines = [PackageVersionInline]


@admin.register(PackageVersion)
class PackageVersionAdmin(admin.ModelAdmin):
    list_display = ["package", "version_number", "created_at"]
