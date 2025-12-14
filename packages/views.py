from typing import Any, Dict, Optional
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404

from .models import Package
from .services import PackageService


class IndexView(TemplateView):
    template_name: str = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Populates the context for the homepage.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        
        # Use Service to get data (clean separation of concerns)
        context['recent_packages'] = PackageService.get_recent_packages(limit=6)
        context['total_packages'] = Package.objects.count()
        context['total_downloads'] = PackageService.get_total_downloads()
        
        return context


class PackageListView(ListView):
    model = Package
    template_name: str = "packages/list.html"
    context_object_name: str = "packages"
    paginate_by: int = 10  # Optional: Adds pagination automatically

    def get_queryset(self) -> QuerySet[Package]:
        """
        Handles filtering (search) and sorting logic.
        """
        queryset: QuerySet[Package] = super().get_queryset()
        
        # 1. Search Logic
        query: Optional[str] = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        # 2. Sort Logic
        sort_param: Optional[str] = self.request.GET.get('sort')
        if sort_param == 'downloads':
            queryset = queryset.order_by('-download_count')
        elif sort_param == 'name':
            queryset = queryset.order_by('name')
        else:
            # Default: Recently updated
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Injects extra context, like the current search query to keep it in the input field.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['current_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', 'updated')
        return context


class PackageDetailView(DetailView):
    model = Package
    template_name: str = "packages/detail.html"
    context_object_name: str = "package"
    
    # Configuration to look up by 'name' instead of 'pk'
    slug_field: str = "name"
    slug_url_kwarg: str = "name"

    def get_object(self, queryset: Optional[QuerySet[Package]] = None) -> Package:
        """
        Override to ensure we fetch by name efficiently.
        """
        if queryset is None:
            queryset = self.get_queryset()
            
        name: str = self.kwargs.get(self.slug_url_kwarg)
        # Using select_related/prefetch_related optimization is good practice here
        # assuming 'versions' is a related model
        return get_object_or_404(queryset.prefetch_related('versions'), name=name)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Render the markdown README before sending to template.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        package: Package = self.object  # type: ignore (DetailView defines self.object)
        
        # Render markdown using the service
        if hasattr(package, 'readme'):
            context['readme_html'] = PackageService.render_markdown(package.readme)
            
        return context
    