from django.db import models
from authentication.models import User


class PackageOS(models.TextChoices):
    LINUX = 'linux', 'Linux'
    WINDOWS = 'windows', 'Windows'
    MACOS = 'macos', 'macOS'
    ANY = 'any', 'Any / Source' # Pour le code source pur ou universel

class PackageArch(models.TextChoices):
    X86_64 = 'x86_64', 'x86_64 (Intel/AMD 64-bit)'
    ARM64 = 'arm64', 'ARM64 (Apple Silicon, RPi)'
    ANY = 'any', 'Any / Universal'


class Package(models.Model):
    name = models.SlugField(unique=True, max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    description = models.TextField(blank=True, help_text="Short description shown in lists")
    license = models.CharField(max_length=50, blank=True, default="MIT")
    repository = models.URLField(blank=True, null=True, help_text="Github/Gitlab URL")
    website = models.URLField(blank=True, null=True)
    
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def latest_version(self):
        """
        Helper pour les templates: {{ package.latest_version }}
        Retourne le numéro de version de la dernière release.
        """
        latest = self.versions.order_by('-created_at').first()
        return latest.version_number if latest else "0.0.0"
    
    @property
    def readme(self):
        """
        Helper pour les templates: {{ package.readme }}
        Affiche le README de la dernière version.
        """
        latest = self.versions.order_by('-created_at').first()
        return latest.readme if latest else ""
    

class PackageVersion(models.Model):
    package = models.ForeignKey(Package, related_name='versions', on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)

    readme = models.TextField(blank=True, help_text="Markdown content extracted from the zip")

    created_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('package', 'version_number')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.package.name} v{self.version_number}"
    

class PackageFile(models.Model):
    version = models.ForeignKey(PackageVersion, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='packages/%Y/%m/')
    os = models.CharField(
        max_length=20, 
        choices=PackageOS.choices, 
        default=PackageOS.ANY
    )
    architecture = models.CharField(
        max_length=20, 
        choices=PackageArch.choices, 
        default=PackageArch.ANY
    )

    download_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('version', 'os', 'architecture')

    def __str__(self):
        return f"{self.version} - {self.os} ({self.architecture})"
    