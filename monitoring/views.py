from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Keyword, Flag
from .serializers import KeywordSerializer, FlagSerializer, FlagUpdateSerializer
from .services import run_scan

class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    http_method_names = ['get', 'post', 'delete']

class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FlagUpdateSerializer
        return FlagSerializer

    http_method_names = ['get', 'patch']

@api_view(['POST'])
def trigger_scan(request):
    """
    Triggers a scan against the external/mock content source.
    """
    source = request.data.get('source', 'mock')
    results = run_scan(source=source)
    return Response({
        "message": "Scan completed.",
        "flags_created_or_updated": results['processed']
    }, status=status.HTTP_200_OK)
