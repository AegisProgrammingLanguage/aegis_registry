from django.db import models
from django.contrib.auth.models import User


class Package(models.Model):
    name = models.SlugField(unique=True, max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class PackageVersion(models.Model):
    package = models.ForeignKey(Package, related_name='versions', on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)

    archive = models.FileField(upload_to='archives')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('package', 'version_number')

    def __str__(self):
        return f"{self.package.name} v{self.version_number}"
    