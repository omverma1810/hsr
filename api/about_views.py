from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Award
from .about_serializers import AwardSerializer
from django.db import transaction

class AwardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Awards.
    """
    queryset = Award.objects.all().order_by('display_order', '-created_at')
    serializer_class = AwardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        """
        Optionally filter by is_active.
        Admin sees all, public sees only is_active=True.
        """
        queryset = super().get_queryset()
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to wrap response."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Awards retrieved successfully'
        })

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to wrap response."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Award retrieved successfully'
        })

    def create(self, request, *args, **kwargs):
        """Override create to wrap response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Award created successfully'
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Override update to wrap response."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Award updated successfully'
        })

    def destroy(self, request, *args, **kwargs):
        """Override destroy to wrap response."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'data': None,
            'message': 'Award deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reorder(self, request):
        """
        Reorder awards.
        Expected body: { "order": [{ "id": 1, "display_order": 1 }, ...] }
        """
        order_data = request.data.get('order', [])
        if not order_data:
            return Response({'success': False, 'error': 'No order data provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                for item in order_data:
                    award_id = item.get('id')
                    display_order = item.get('display_order')
                    if award_id is not None and display_order is not None:
                        Award.objects.filter(id=award_id).update(display_order=display_order)
            
            return Response({'success': True, 'message': 'Awards reordered successfully'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

