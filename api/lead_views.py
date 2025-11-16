"""
Views for Lead Management (Phase 5).
Handles lead CRUD operations with priority, follow-ups, and analytics.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponse
import csv
from datetime import timedelta

from .models import Lead, Project, AdminUser
from .lead_serializers import (
    LeadListSerializer,
    LeadDetailSerializer,
    LeadCreateSerializer,
    LeadUpdateSerializer,
    LeadStatusUpdateSerializer,
    LeadAddNoteSerializer,
    LeadStatisticsSerializer,
    BulkLeadActionSerializer,
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class LeadsListView(APIView):
    """
    GET: List all leads with filtering, search, sorting, pagination (admin only)
    POST: Create new lead (public - contact form)
    """

    def get_permissions(self):
        """Admin only for GET, public for POST."""
        if self.request.method == 'GET':
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        """Get all leads with advanced filtering and pagination (admin only)."""
        try:
            # Query parameters
            status_filter = request.query_params.get('status')
            priority = request.query_params.get('priority')
            source = request.query_params.get('source')
            project_id = request.query_params.get('project')
            contacted_by = request.query_params.get('contacted_by')
            search = request.query_params.get('search')
            overdue_only = request.query_params.get('overdue_only')
            sort_by = request.query_params.get('sort_by', '-created_at')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 25))

            # Validate page_size
            if page_size not in [10, 25, 50, 100]:
                page_size = 25

            # Start with all non-deleted leads
            queryset = Lead.objects.select_related(
                'project',
                'contacted_by'
            ).all()

            # Apply filters
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            if priority:
                queryset = queryset.filter(priority=priority)

            if source:
                queryset = queryset.filter(source=source)

            if project_id:
                queryset = queryset.filter(project_id=project_id)

            if contacted_by:
                queryset = queryset.filter(contacted_by_id=contacted_by)

            if overdue_only and overdue_only.lower() == 'true':
                queryset = queryset.filter(
                    next_follow_up__isnull=False,
                    next_follow_up__lt=timezone.now()
                )

            # Search
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(message__icontains=search) |
                    Q(project__title__icontains=search)
                )

            # Sorting
            allowed_sort_fields = [
                'created_at', '-created_at',
                'priority', '-priority',
                'status', '-status',
                'next_follow_up', '-next_follow_up',
                'name', '-name',
            ]
            if sort_by in allowed_sort_fields:
                queryset = queryset.order_by(sort_by)

            # Count before pagination
            total = queryset.count()

            # Pagination
            start = (page - 1) * page_size
            end = start + page_size
            leads = queryset[start:end]

            # Serialize
            serializer = LeadListSerializer(leads, many=True)

            return success_response(
                data={
                    'leads': serializer.data,
                    'pagination': {
                        'total': total,
                        'page': page,
                        'page_size': page_size,
                        'total_pages': (total + page_size - 1) // page_size,
                    }
                },
                message='Leads retrieved successfully'
            )

        except Exception as e:
            return error_response(
                message='Failed to retrieve leads',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create new lead from contact form (public)."""
        try:
            serializer = LeadCreateSerializer(data=request.data)

            if serializer.is_valid():
                lead = serializer.save()

                # Return simple success for public endpoint
                return success_response(
                    data={'id': lead.id},
                    message='Thank you for your inquiry! We will contact you soon.',
                    status_code=status.HTTP_201_CREATED
                )

            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message='Failed to submit inquiry',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadDetailView(APIView):
    """
    GET: Get single lead details (admin only)
    PUT: Update lead (admin only)
    DELETE: Delete lead (admin only, soft delete)
    """

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        """Get lead details."""
        try:
            lead = Lead.objects.select_related(
                'project',
                'contacted_by'
            ).get(pk=pk)
            serializer = LeadDetailSerializer(lead)

            return success_response(
                data=serializer.data,
                message='Lead retrieved successfully'
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to retrieve lead',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """Update lead (admin only)."""
        try:
            lead = Lead.objects.get(pk=pk)
            serializer = LeadUpdateSerializer(
                lead,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()

                # Return detailed response
                detail_serializer = LeadDetailSerializer(lead)
                return success_response(
                    data=detail_serializer.data,
                    message='Lead updated successfully'
                )

            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to update lead',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """Soft delete lead (admin only)."""
        try:
            lead = Lead.objects.get(pk=pk)
            lead.soft_delete()

            return success_response(
                data={'id': pk},
                message='Lead deleted successfully'
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to delete lead',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadStatusUpdateView(APIView):
    """POST: Update lead status with automatic tracking (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        """Update lead status and track changes."""
        try:
            lead = Lead.objects.get(pk=pk)
            serializer = LeadStatusUpdateSerializer(data=request.data)

            if not serializer.is_valid():
                return error_response(
                    message='Validation failed',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            next_follow_up = serializer.validated_data.get('next_follow_up')

            # Update status
            old_status = lead.status
            lead.status = new_status

            # If changing to contacted, mark as contacted
            if new_status == 'contacted' and old_status != 'contacted':
                lead.mark_contacted(admin_user=request.user)

            # Add notes if provided
            if notes:
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                note_entry = f"\n[{timestamp}] Status changed from '{old_status}' to '{new_status}': {notes}"
                lead.notes += note_entry

            # Update follow-up if provided
            if next_follow_up:
                lead.next_follow_up = next_follow_up

            lead.save()

            # Return detailed response
            detail_serializer = LeadDetailSerializer(lead)
            return success_response(
                data=detail_serializer.data,
                message=f'Lead status updated to {new_status}'
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to update lead status',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadAddNoteView(APIView):
    """POST: Add note to lead (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        """Add note to lead."""
        try:
            lead = Lead.objects.get(pk=pk)
            serializer = LeadAddNoteSerializer(data=request.data)

            if not serializer.is_valid():
                return error_response(
                    message='Validation failed',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            note = serializer.validated_data['note']
            next_follow_up = serializer.validated_data.get('next_follow_up')

            # Add note with timestamp and user
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            note_entry = f"\n[{timestamp}] {request.user.full_name}: {note}"
            lead.notes += note_entry

            # Update follow-up if provided
            if next_follow_up:
                lead.next_follow_up = next_follow_up

            lead.save()

            # Return detailed response
            detail_serializer = LeadDetailSerializer(lead)
            return success_response(
                data=detail_serializer.data,
                message='Note added successfully'
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to add note',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadRestoreView(APIView):
    """POST: Restore soft-deleted lead (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        """Restore soft-deleted lead."""
        try:
            lead = Lead.all_objects.get(pk=pk)

            if not lead.is_deleted:
                return error_response(
                    message='Lead is not deleted',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            lead.restore()

            # Return detailed response
            detail_serializer = LeadDetailSerializer(lead)
            return success_response(
                data=detail_serializer.data,
                message='Lead restored successfully'
            )

        except Lead.DoesNotExist:
            return error_response(
                message='Lead not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to restore lead',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadStatisticsView(APIView):
    """GET: Get lead statistics and analytics (admin only)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        """Get comprehensive lead statistics."""
        try:
            # All non-deleted leads
            all_leads = Lead.objects.all()
            total_leads = all_leads.count()

            # Status breakdown
            new_leads = all_leads.filter(status='new').count()
            contacted_leads = all_leads.filter(status='contacted').count()
            qualified_leads = all_leads.filter(status='qualified').count()
            closed_leads = all_leads.filter(status='closed').count()

            # Conversion rates
            contact_rate = (contacted_leads / total_leads * 100) if total_leads > 0 else 0
            qualification_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
            close_rate = (closed_leads / total_leads * 100) if total_leads > 0 else 0

            # Priority breakdown
            urgent_leads = all_leads.filter(priority='urgent').count()
            high_priority_leads = all_leads.filter(priority='high').count()
            medium_priority_leads = all_leads.filter(priority='medium').count()
            low_priority_leads = all_leads.filter(priority='low').count()

            # Follow-up stats
            leads_with_follow_up = all_leads.filter(next_follow_up__isnull=False).count()
            overdue_follow_ups = all_leads.filter(
                next_follow_up__isnull=False,
                next_follow_up__lt=timezone.now()
            ).count()

            # Source breakdown
            source_stats = all_leads.values('source').annotate(count=Count('id'))
            source_breakdown = {item['source']: item['count'] for item in source_stats}

            # Time-based stats
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=today_start.weekday())
            month_start = today_start.replace(day=1)

            leads_today = all_leads.filter(created_at__gte=today_start).count()
            leads_this_week = all_leads.filter(created_at__gte=week_start).count()
            leads_this_month = all_leads.filter(created_at__gte=month_start).count()

            # Prepare statistics data
            statistics_data = {
                'total_leads': total_leads,
                'new_leads': new_leads,
                'contacted_leads': contacted_leads,
                'qualified_leads': qualified_leads,
                'closed_leads': closed_leads,
                'contact_rate': round(contact_rate, 2),
                'qualification_rate': round(qualification_rate, 2),
                'close_rate': round(close_rate, 2),
                'urgent_leads': urgent_leads,
                'high_priority_leads': high_priority_leads,
                'medium_priority_leads': medium_priority_leads,
                'low_priority_leads': low_priority_leads,
                'leads_with_follow_up': leads_with_follow_up,
                'overdue_follow_ups': overdue_follow_ups,
                'source_breakdown': source_breakdown,
                'leads_today': leads_today,
                'leads_this_week': leads_this_week,
                'leads_this_month': leads_this_month,
            }

            serializer = LeadStatisticsSerializer(data=statistics_data)
            serializer.is_valid()

            return success_response(
                data=serializer.data,
                message='Lead statistics retrieved successfully'
            )

        except Exception as e:
            return error_response(
                message='Failed to retrieve lead statistics',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkLeadActionsView(APIView):
    """POST: Perform bulk actions on leads (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        """Perform bulk actions on multiple leads."""
        try:
            serializer = BulkLeadActionSerializer(data=request.data)

            if not serializer.is_valid():
                return error_response(
                    message='Validation failed',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            lead_ids = serializer.validated_data['lead_ids']
            action = serializer.validated_data['action']

            # Get leads
            if action in ['delete', 'change_status', 'change_priority', 'assign_contact']:
                leads = Lead.objects.filter(id__in=lead_ids)
            else:  # restore
                leads = Lead.all_objects.filter(id__in=lead_ids)

            if not leads.exists():
                return error_response(
                    message='No leads found with provided IDs',
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Perform action
            updated_count = 0

            if action == 'delete':
                for lead in leads:
                    lead.soft_delete()
                    updated_count += 1

            elif action == 'restore':
                for lead in leads:
                    if lead.is_deleted:
                        lead.restore()
                        updated_count += 1

            elif action == 'change_status':
                new_status = serializer.validated_data['status']
                updated_count = leads.update(status=new_status)

            elif action == 'change_priority':
                new_priority = serializer.validated_data['priority']
                updated_count = leads.update(priority=new_priority)

            elif action == 'assign_contact':
                contacted_by_id = serializer.validated_data['contacted_by']
                try:
                    admin_user = AdminUser.objects.get(id=contacted_by_id)
                    updated_count = leads.update(contacted_by=admin_user)
                except AdminUser.DoesNotExist:
                    return error_response(
                        message='Admin user not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )

            return success_response(
                data={
                    'action': action,
                    'updated_count': updated_count,
                    'lead_ids': lead_ids,
                },
                message=f'Bulk action "{action}" completed successfully on {updated_count} leads'
            )

        except Exception as e:
            return error_response(
                message='Failed to perform bulk action',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportLeadsView(APIView):
    """GET: Export leads to CSV (admin only)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        """Export leads to CSV file."""
        try:
            # Get all leads (apply same filters as list view if needed)
            status_filter = request.query_params.get('status')
            priority = request.query_params.get('priority')
            source = request.query_params.get('source')

            queryset = Lead.objects.select_related('project', 'contacted_by').all()

            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if priority:
                queryset = queryset.filter(priority=priority)
            if source:
                queryset = queryset.filter(source=source)

            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="leads_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

            writer = csv.writer(response)

            # Write header
            writer.writerow([
                'ID',
                'Name',
                'Email',
                'Phone',
                'Project',
                'Message',
                'Status',
                'Priority',
                'Source',
                'Preferred Contact',
                'Next Follow-up',
                'Follow-up Count',
                'Contacted At',
                'Contacted By',
                'Notes',
                'Created At',
            ])

            # Write data
            for lead in queryset:
                writer.writerow([
                    lead.id,
                    lead.name,
                    lead.email,
                    lead.phone,
                    lead.project.title if lead.project else '',
                    lead.message,
                    lead.status,
                    lead.priority,
                    lead.source,
                    lead.preferred_contact_method,
                    lead.next_follow_up.strftime('%Y-%m-%d %H:%M') if lead.next_follow_up else '',
                    lead.follow_up_count,
                    lead.contacted_at.strftime('%Y-%m-%d %H:%M') if lead.contacted_at else '',
                    lead.contacted_by.full_name if lead.contacted_by else '',
                    lead.notes.replace('\n', ' | '),
                    lead.created_at.strftime('%Y-%m-%d %H:%M'),
                ])

            return response

        except Exception as e:
            return error_response(
                message='Failed to export leads',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
