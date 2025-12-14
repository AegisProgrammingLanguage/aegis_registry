import zipfile
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpRequest
from django.db.models import F
from typing import Optional

from .models import Package, PackageVersion, PackageFile, PackageOS, PackageArch
from .serializers import PackageSerializer

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    lookup_field = 'name'

    parser_classes = (MultiPartParser, FormParser)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def publish(self, request: HttpRequest, name: Optional[str] = None) -> Response:
        """
        Publie un nouveau fichier. Utilise PackageUploadSerializer pour valider les données.
        """
        package: Package = self.get_object()

        # 1. Vérification Propriétaire
        if package.author != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        # 2. VALIDATION VIA SERIALIZER
        # On passe les données au serializer pour vérifier la taille, le format version, etc.
        serializer = PackageUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Si invalide, on renvoie les erreurs précises (ex: "File too large")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 3. Récupération des données propres et validées
        version_num = serializer.validated_data['version']
        archive_file = serializer.validated_data['file']
        target_os = serializer.validated_data.get('os', PackageOS.ANY)
        target_arch = serializer.validated_data.get('architecture', PackageArch.ANY)
        
        # 4. Gestion de la Version (Get or Create)
        version, created = PackageVersion.objects.get_or_create(
            package=package,
            version_number=version_num
        )
        
        # Extraction du README (si nouvelle version ou readme vide)
        if created or not version.readme:
            readme_content = self._extract_readme_from_zip(archive_file)
            if readme_content:
                version.readme = readme_content
                version.save()
        
        # 5. Vérification de conflit (Fichier déjà existant pour cet OS/Arch ?)
        if PackageFile.objects.filter(version=version, os=target_os, architecture=target_arch).exists():
            return Response({
                "error": f"File for OS '{target_os}' and Arch '{target_arch}' already exists in version {version_num}"
            }, status=status.HTTP_409_CONFLICT)

        # 6. Création du fichier
        PackageFile.objects.create(
            version=version,
            file=archive_file,
            os=target_os,
            architecture=target_arch
        )
        
        # Mise à jour de la date de modification du paquet global
        package.save() 

        msg = "Version created and file uploaded" if created else "File added to existing version"
        
        return Response({
            "status": msg,
            "version": version_num,
            "os": target_os,
            "arch": target_arch,
            "readme_extracted": bool(version.readme)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["get"])
    def latest(self, request: HttpRequest, name: Optional[str] = None) -> Response:
        """
        Retrieves the download URL for the latest version.
        Accepts ?os=...&architecture=... to target a specific binary.
        Increments download counts.
        """
        package: Package = self.get_object()
        
        # 1. Find latest version
        latest_version: PackageVersion = package.versions.order_by('-created_at').first()
        if not latest_version:
            return Response({"error": "No versions found"}, status=status.HTTP_404_NOT_FOUND)
        
        # 2. Client preferences
        req_os = request.query_params.get('os', PackageOS.ANY)
        req_arch = request.query_params.get('architecture', PackageArch.ANY)

        # 3. Resolution Strategy
        
        # A. Exact Match (Optimized Binary)
        target_file = PackageFile.objects.filter(
            version=latest_version, 
            os=req_os, 
            architecture=req_arch
        ).first()

        # B. Fallback: Source Code (Any/Any)
        if not target_file:
            target_file = PackageFile.objects.filter(
                version=latest_version,
                os=PackageOS.ANY,
                architecture=PackageArch.ANY
            ).first()
        
        # C. Total Failure
        if not target_file:
            return Response({
                "error": f"No compatible asset found for {req_os}/{req_arch} in version {latest_version.version_number}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # --- STATS INCREMENT ---
        # We use F expressions to avoid race conditions
        Package.objects.filter(pk=package.pk).update(download_count=F('download_count') + 1)
        PackageVersion.objects.filter(pk=latest_version.pk).update(download_count=F('download_count') + 1)
        PackageFile.objects.filter(pk=target_file.pk).update(download_count=F('download_count') + 1)

        # 4. Response
        return Response({
            "version": latest_version.version_number,
            "url": request.build_absolute_uri(target_file.file.url),
            "asset_type": "binary" if target_file.os != PackageOS.ANY else "source"
        })

    def _extract_readme_from_zip(self, uploaded_file) -> Optional[str]:
        """
        Helper method to open the uploaded zip and find a README file.
        Returns the content string or None.
        """
        try:
            # We must verify it's a valid zip
            if not zipfile.is_zipfile(uploaded_file):
                return None
            
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                # Look for files containing 'readme' (case insensitive)
                # We prioritize root files, but accept nested ones if needed
                for filename in z.namelist():
                    if "readme" in filename.lower() and (filename.endswith('.md') or filename.endswith('.txt')):
                        
                        # Read and decode
                        with z.open(filename) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            
                        # Important: Reset file pointer for the subsequent save() model call
                        uploaded_file.seek(0)
                        return content
                        
            # Reset pointer even if nothing found
            uploaded_file.seek(0)
        except Exception as e:
            print(f"Error extracting readme: {e}")
            # Ensure pointer is reset in case of error
            uploaded_file.seek(0)
            return None
        
        return None
    