from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
import csv
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Lead, Project
from .lead_serializers import LeadSerializer, LeadListSerializer
from .utils import success_response, error_response
from .permissions import IsAdminUser


class LeadsListView(APIView):
    """List and create leads."""
    
    def get_permissions(self):
        """Public POST (for contact forms), admin GET."""
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('status', str, description='Filter by status (new/contacted/qualified/closed)'),
            OpenApiParameter('source', str, description='Filter by source (contact_form/whatsapp/phone_call/walk_in)'),
            OpenApiParameter('project_id', int, description='Filter by project ID'),
            OpenApiParameter('search', str, description='Search in name, email, phone, message'),
            OpenApiParameter('page', int, description='Page number'),
            OpenApiParameter('page_size', int, description='Items per page (10/25/50/100)'),
            OpenApiParameter('include_deleted', bool, description='Include deleted leads (admin only)'),
        ],
        responses={200: LeadListSerializer(many=True)},
        description="List all leads with filtering and pagination"
    )
    def get(self, request):
        """List leads with filtering."""
        try:
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            if include_deleted and request.user.is_authenticated and request.user.is_staff:
                queryset = Lead.all_objects.all()
            else:
                queryset = Lead.objects.all()
            
            # Filtering
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            source_filter = request.query_params.get('source')
            if source_filter:
                queryset = queryset.filter(source=source_filter)
            
            project_id = request.query_params.get('project_id')
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            # Searching
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(message__icontains=search)
                )
            
            # Ordering
            queryset = queryset.select_related('project', 'contacted_by').order_by('-created_at')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 25))
            
            valid_page_sizes = [10, 25, 50, 100]
            if page_size not in valid_page_sizes:
                page_size = 25
            
            paginator = Paginator(queryset, page_size)
            
            try:
                leads_page = paginator.page(page)
            except EmptyPage:
                leads_page = paginator.page(paginator.num_pages)
            
            serializer = LeadListSerializer(leads_page.object_list, many=True)
            
            return success_response(
                data={
                    'results': serializer.data,
                    'pagination': {
                        'current_page': leads_page.number,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'page_size': page_size,
                        'has_next': leads_page.has_next(),
                        'has_previous': leads_page.has_previous(),
                    }
                },
                message=f"Retrieved {len(serializer.data)} leads"
            )
        
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve leads"
            )
    
    @extend_schema(
        request=LeadSerializer,
        responses={201: LeadSerializer},
        description="Create a new lead (public access for contact forms)"
    )
    def post(self, request):
        """Create a new lead."""
        try:
            serializer = LeadSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                lead = serializer.save()
                response_serializer = LeadSerializer(lead)
                return success_response(
                    data=response_serializer.data,
                    message="Lead created successfully",
                    status_code=status.HTTP_201_CREATED
                )
            
            return error_response(
                errors=serializer.errors,
                message="Failed to create lead"
            )
        
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to create lead"
            )


class LeadDetailView(APIView):
    """Retrieve, update, or delete a lead."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_object(self, pk, include_deleted=False):
        """Get lead by ID."""
        try:
            if include_deleted:
                return Lead.all_objects.select_related('project', 'contacted_by').get(pk=pk)
            return Lead.objects.select_related('project', 'contacted_by').get(pk=pk)
        except Lead.DoesNotExist:
            return None
    
    @extend_schema(
        responses={200: LeadSerializer},
        description="Get lead details (admin only)"
    )
    def get(self, request, pk):
        """Get lead details."""
        lead = self.get_object(pk)
        if not lead:
            return error_response(
                errors={'detail': 'Lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LeadSerializer(lead)
        return success_response(
            data=serializer.data,
            message="Lead retrieved successfully"
        )
    
    @extend_schema(
        request=LeadSerializer,
        responses={200: LeadSerializer},
        description="Update lead (admin only)"
    )
    def put(self, request, pk):
        """Update lead."""
        lead = self.get_object(pk)
        if not lead:
            return error_response(
                errors={'detail': 'Lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LeadSerializer(lead, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            lead = serializer.save()
            response_serializer = LeadSerializer(lead)
            return success_response(
                data=response_serializer.data,
                message="Lead updated successfully"
            )
        
        return error_response(
            errors=serializer.errors,
            message="Failed to update lead"
        )
    
    patch = put  # Support both PUT and PATCH
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Lead deleted successfully")},
        description="Delete lead (admin only, soft delete)"
    )
    def delete(self, request, pk):
        """Delete lead (soft delete)."""
        lead = self.get_object(pk)
        if not lead:
            return error_response(
                errors={'detail': 'Lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            lead.soft_delete()
            return success_response(
                message="Lead deleted successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to delete lead"
            )


class LeadStatusView(APIView):
    """Update lead status."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        request={'status': 'string'},
        responses={200: LeadSerializer},
        description="Update lead status (admin only)"
    )
    def post(self, request, pk):
        """Update lead status."""
        try:
            lead = Lead.objects.get(pk=pk, is_deleted=False)
            new_status = request.data.get('status')
            
            if not new_status:
                return error_response(
                    errors={'status': 'Status is required'},
                    message="Status is required"
                )
            
            valid_statuses = ['new', 'contacted', 'qualified', 'closed']
            if new_status not in valid_statuses:
                return error_response(
                    errors={'status': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                    message="Invalid status"
                )
            
            # Update contacted_at when status changes to contacted
            if new_status == 'contacted' and lead.status != 'contacted':
                from django.utils import timezone
                lead.contacted_at = timezone.now()
                lead.contacted_by = request.user
            
            lead.status = new_status
            lead.save()
            
            serializer = LeadSerializer(lead)
            return success_response(
                data=serializer.data,
                message="Lead status updated successfully"
            )
        
        except Lead.DoesNotExist:
            return error_response(
                errors={'detail': 'Lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update lead status"
            )


class LeadRestoreView(APIView):
    """Restore a soft-deleted lead."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='Lead restored successfully - Returns the restored lead details.'),
            404: OpenApiResponse(description='Not found - Deleted lead does not exist.'),
        },
        description='''
        **Restore Lead**
        
        Restore a soft-deleted lead. This will set `is_deleted=False` and make the lead visible again in the leads list.
        
        **Use Cases:**
        - Recover accidentally deleted leads
        - Restore leads from trash
        
        **Note:** Only soft-deleted leads can be restored. If a lead was never deleted, you'll get a 404 error.
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['Leads']
    )
    def post(self, request, pk):
        """Restore lead."""
        try:
            lead = Lead.all_objects.get(pk=pk, is_deleted=True)
            lead.restore()
            serializer = LeadSerializer(lead)
            return success_response(
                data=serializer.data,
                message="Lead restored successfully"
            )
        except Lead.DoesNotExist:
            return error_response(
                errors={'detail': 'Deleted lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to restore lead"
            )


class LeadNotesView(APIView):
    """Add or update lead notes."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        request={'notes': 'string'},
        responses={200: LeadSerializer},
        description="Update lead notes (admin only)"
    )
    def post(self, request, pk):
        """Update lead notes."""
        try:
            lead = Lead.objects.get(pk=pk, is_deleted=False)
            notes = request.data.get('notes', '')
            lead.notes = notes
            lead.save()
            
            serializer = LeadSerializer(lead)
            return success_response(
                data=serializer.data,
                message="Lead notes updated successfully"
            )
        except Lead.DoesNotExist:
            return error_response(
                errors={'detail': 'Lead not found'},
                message="Lead not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update lead notes"
            )


class BulkLeadsActionView(APIView):
    """Bulk actions on leads."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        request={
            'lead_ids': [int],
            'action': 'string',
            'status': 'string (optional)'
        },
        responses={200: OpenApiResponse(description="Bulk action completed")},
        description="Perform bulk actions on leads (admin only)"
    )
    def post(self, request):
        """Perform bulk actions."""
        try:
            lead_ids = request.data.get('lead_ids', [])
            action = request.data.get('action')
            
            if not lead_ids:
                return error_response(
                    errors={'lead_ids': 'Lead IDs are required'},
                    message="Lead IDs are required"
                )
            
            if not action:
                return error_response(
                    errors={'action': 'Action is required'},
                    message="Action is required"
                )
            
            leads = Lead.objects.filter(id__in=lead_ids, is_deleted=False)
            
            if action == 'delete':
                count = 0
                for lead in leads:
                    lead.soft_delete()
                    count += 1
                return success_response(
                    data={'count': count},
                    message=f"{count} lead(s) deleted successfully"
                )
            
            elif action == 'restore':
                deleted_leads = Lead.all_objects.filter(id__in=lead_ids, is_deleted=True)
                count = 0
                for lead in deleted_leads:
                    lead.restore()
                    count += 1
                return success_response(
                    data={'count': count},
                    message=f"{count} lead(s) restored successfully"
                )
            
            elif action == 'change_status':
                new_status = request.data.get('status')
                if not new_status:
                    return error_response(
                        errors={'status': 'Status is required for change_status action'},
                        message="Status is required"
                    )
                
                valid_statuses = ['new', 'contacted', 'qualified', 'closed']
                if new_status not in valid_statuses:
                    return error_response(
                        errors={'status': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                        message="Invalid status"
                    )
                
                from django.utils import timezone
                count = 0
                for lead in leads:
                    if new_status == 'contacted' and lead.status != 'contacted':
                        lead.contacted_at = timezone.now()
                        lead.contacted_by = request.user
                    lead.status = new_status
                    lead.save()
                    count += 1
                
                return success_response(
                    data={'count': count},
                    message=f"{count} lead(s) status updated successfully"
                )
            
            else:
                return error_response(
                    errors={'action': f'Invalid action. Must be one of: delete, restore, change_status'},
                    message="Invalid action"
                )
        
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to perform bulk action"
            )


class ExportLeadsView(APIView):
    """Export leads to CSV."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('status', str, description='Filter by status'),
            OpenApiParameter('source', str, description='Filter by source'),
        ],
        responses={200: OpenApiResponse(description="CSV file download")},
        description="Export leads to CSV (admin only)"
    )
    def get(self, request):
        """Export leads to CSV."""
        try:
            queryset = Lead.objects.all()
            
            # Apply filters
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            source_filter = request.query_params.get('source')
            if source_filter:
                queryset = queryset.filter(source=source_filter)
            
            queryset = queryset.select_related('project').order_by('-created_at')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Name', 'Email', 'Phone', 'Project', 'Message', 
                'Source', 'Status', 'Contacted At', 'Notes', 'Created At'
            ])
            
            for lead in queryset:
                writer.writerow([
                    lead.id,
                    lead.name,
                    lead.email,
                    lead.phone,
                    lead.project.title if lead.project else '',
                    lead.message,
                    lead.get_source_display(),
                    lead.get_status_display(),
                    lead.contacted_at.strftime('%Y-%m-%d %H:%M:%S') if lead.contacted_at else '',
                    lead.notes,
                    lead.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to export leads"
            )


class LeadsStatisticsView(APIView):
    """Get leads statistics."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Leads statistics")},
        description="Get leads statistics (admin only)"
    )
    def get(self, request):
        """Get leads statistics."""
        try:
            queryset = Lead.objects.filter(is_deleted=False)
            
            statistics = {
                'total_leads': queryset.count(),
                'new_leads': queryset.filter(status='new').count(),
                'contacted_leads': queryset.filter(status='contacted').count(),
                'qualified_leads': queryset.filter(status='qualified').count(),
                'closed_leads': queryset.filter(status='closed').count(),
            }
            
            return success_response(
                data=statistics,
                message="Leads statistics retrieved successfully"
            )
        
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve leads statistics"
            )

