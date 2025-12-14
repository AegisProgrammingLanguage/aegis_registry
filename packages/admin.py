from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Package, PackageVersion, PackageFile


# 1. Inline pour les fichiers (s'affichera dans le détail d'une Version)
class PackageFileInline(TabularInline):
    model = PackageFile
    extra = 1  # Propose une ligne vide par défaut pour uploader un fichier
    tab = True # Optionnel Unfold : rend l'inline plus joli
    fields = ["file", "os", "architecture", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


# 2. Inline pour les versions (s'affichera dans le détail d'un Package)
class PackageVersionInline(TabularInline):
    model = PackageVersion
    extra = 0
    tab = True
    show_change_link = True 
    fields = ["version_number", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Package)
class PackageAdmin(ModelAdmin):
    list_display = ["name", "author", "description", "created_at"]
    search_fields = ["name", "author__username"]
    inlines = [PackageVersionInline]


@admin.register(PackageVersion)
class PackageVersionAdmin(ModelAdmin):
    list_display = ["package", "version_number", "created_at"]
    list_filter = ["package", "created_at"]
    search_fields = ["package__name", "version_number"]
    inlines = [PackageFileInline]


@admin.register(PackageFile)
class PackageFileAdmin(ModelAdmin):
    list_display = ["version__package", "version__version_number", "os", "architecture", "uploaded_at"]
    