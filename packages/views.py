from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Package, PackageVersion
from .serializers import PackageSerializer, VersionSerializer
from django.http import HttpRequest
from typing import Optional


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    lookup_field = 'name'

    parser_classes = (MultiPartParser, FormParser)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def publish(self, request: HttpRequest, name: Optional[str] = None) -> Response:
        package: Package = self.get_object()

        # Check ownership
        if package.author != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        version_num = request.data.get("version")
        archive_file = request.data.get("file")

        if not version_num or not archive_file:
            return Response({
                "error": "Version and file required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Version
        if PackageVersion.objects.filter(package=package, version_number=version_num).exists():
            return Response({
                "error": "Version already exists"
            }, status=status.HTTP_409_CONFLICT)
        
        PackageVersion.objects.create(
            package=package,
            version_number=version_num,
            archive=archive_file
        )

        return Response({
            "status": "Published!"
        }, status=status.HTTP_201_CREATED)
    
    # Endpoint custom pour récupérer la dernière version directement
    @action(detail=True, methods=["get"])
    def latest(self, request: HttpRequest, name: Optional[str] = None) -> Response:
        package: Package = self.get_object()
        latest: PackageVersion = package.versions.order_by('-created_at').first()
        if not latest:
            return Response({"error": "No versions found"}, status=404)
        
        return Response({
            "version": latest.version_number,
            "url": request.build_absolute_uri(latest.archive.url)
        })
