import re
from rest_framework import serializers
from .models import Package, PackageVersion, PackageFile

# Liste des noms réservés pour le système ou les futures libs standard
RESERVED_NAMES = [
    'aegis', 'std', 'core', 'math', 'http', 'net', 'io', 'system', 
    'admin', 'root', 'test', 'official', 'registry', 'config', 'user'
]

class VersionSerializer(serializers.ModelSerializer):
    """
    Sert à afficher les versions imbriquées dans la liste des paquets.
    """
    class Meta:
        model = PackageVersion
        fields = ["version_number", "created_at", "download_count"]


class PackageSerializer(serializers.ModelSerializer):
    """
    Utilisé pour lister les paquets et créer un NOUVEAU paquet (le conteneur).
    """
    versions = VersionSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Package
        fields = ['id', 'name', 'author', 'description', 'versions', 'created_at', 'download_count']
        read_only_fields = ['author', 'created_at', 'download_count', 'versions']

    def validate_name(self, value):
        """
        Validation stricte du nom du paquet à la création.
        """
        value = value.lower().strip()
        
        # 1. Regex : Uniquement lettres minuscules, chiffres et underscores
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError("Package name can only contain lowercase letters, numbers, and underscores.")

        # 2. Longueur minimale
        if len(value) < 3:
            raise serializers.ValidationError("Package name must be at least 3 characters long.")

        # 3. Noms réservés
        if value in RESERVED_NAMES:
            raise serializers.ValidationError(f"The name '{value}' is reserved by the Aegis Registry.")

        # 4. Unicité (déjà géré par le modèle unique=True, mais message plus propre ici)
        if Package.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Package '{value}' already exists.")

        return value


class PackageUploadSerializer(serializers.Serializer):
    """
    Serializer SPÉCIFIQUE pour l'action 'publish'.
    Il ne valide pas un modèle entier, mais les inputs de la commande CLI.
    """
    name = serializers.SlugField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)

    version = serializers.CharField(max_length=20)
    file = serializers.FileField()
    os = serializers.CharField(required=False, default="any")
    architecture = serializers.CharField(required=False, default="any")

    def validate_name(self, value):
        value = value.lower().strip()
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError("Invalid name format.")
        if value in RESERVED_NAMES:
            raise serializers.ValidationError(f"The name '{value}' is reserved.")
        return value

    def validate_version(self, value):
        """Force le format SemVer (X.Y.Z)"""
        # Accepte 1.0.0 ou 1.0.0-beta, mais refuse "toto" ou "v1"
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$', value):
            raise serializers.ValidationError("Version must follow SemVer format (e.g., 1.0.0 or 1.0.2-beta)")
        return value

    def validate_file(self, value):
        """Sécurité sur le fichier uploadé"""
        # 1. Vérification de l'extension
        if not value.name.endswith('.zip'):
             raise serializers.ValidationError("Only .zip files are allowed.")

        # 2. Limite de taille (ex: 50 MB)
        limit_mb = 50
        if value.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File too large. Size should not exceed {limit_mb} MB.")
             
        return value
    