from typing import  Dict, Optional
from django.db.models import Sum, QuerySet
from .models import Package
import markdown


class PackageService:
    """
    Service layer to handle business logic for Packages.
    Separates DB queries and data processing from the View layer.
    """

    @staticmethod
    def get_total_downloads() -> int:
        """Calculates the sum of downloads across all packages."""
        result: Dict[str, int] = Package.objects.aggregate(total=Sum('download_count'))
        return result.get('total') or 0

    @staticmethod
    def get_recent_packages(limit: int = 6) -> QuerySet[Package]:
        return Package.objects.order_by('-updated_at')[:limit]

    @staticmethod
    def render_markdown(text: Optional[str]) -> str:
        """Safely renders markdown content to HTML."""
        if not text:
            return ""
        # Using extensions for code highlighting and tables
        return markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])
    