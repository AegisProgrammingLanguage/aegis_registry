from rest_framework import serializers
from .models import Package, PackageVersion


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageVersion
        fields = ["version_number", "archive", "created_at"]


class PackageSerializer(serializers.ModelSerializer):
    versions = VersionSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Package
        fields = ['id', 'name', 'author', 'description', 'versions', 'created_at']
        