import os
import textwrap
from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from Accounts.models import StudentProfile
from .models import Complaint, ComplaintCategory, ComplaintUpdate
import uuid

# PDF generation imports
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# Create your views here.
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'User does not exist. Please sign up.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
        else:
            # Start session
            login(request, user)
            request.session['username'] = user.username
            request.session.save()
            # Redirect to home page to show user's complaints
            return redirect('home')
    return render(request, 'login.html')


def logout_page(request):
    logout(request)
    return render(request, 'login.html')


def signup_page(request):
    if request.method == 'POST':
        name = request.POST.get('signupName')
        username = request.POST.get('signupUsername')
        email = request.POST.get('signupEmail')
        password = request.POST.get('signupPassword')
        division = request.POST.get('signupDivision')

        if not division:
            messages.info(request, 'Division is required to complete signup.')
            return render(request, 'signup.html')

        user = User.objects.filter(username=username)
        if user.exists():
            messages.info(request, 'Username already exists')
            return render(request, 'signup.html')

        if email and User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return render(request, 'signup.html')

        if email and User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return render(request, 'signup.html')

        user = User.objects.create_user(
            first_name=name,
            username=username,
            email=email if email else '',
        )
        user.set_password(password)
        user.save()

        StudentProfile.objects.update_or_create(
            user=user,
            defaults={'division': division}
        )

        messages.info(request, "user created successfully")

    return render(request, 'signup.html')


@login_required(login_url='/')
def home(request):
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint')
        complaint_img = request.FILES.get('complaint_img')
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')

        profile, _ = StudentProfile.objects.get_or_create(user=request.user, defaults={'division': ''})
        if not profile.division:
            messages.error(request, 'Division information is missing. Please contact support to update your profile.')
            return redirect('home')

        display_name = (request.user.first_name or '').strip() or request.user.username

        # Get category object if provided
        category = None
        if category_id:
            try:
                category = ComplaintCategory.objects.get(id=category_id)
            except ComplaintCategory.DoesNotExist:
                pass

        # Create complaint using Django ORM
        complaint_obj = Complaint.objects.create(
            user=request.user,
            name=display_name,
            division=profile.division,
            complaint=complaint_text,
            complaint_img=complaint_img,
            category=category,
            priority=priority
        )

        # Send confirmation email to user
        if request.user.email:
            subject = f'Complaint #{complaint_obj.id} Submitted Successfully'
            message = (
                f"Hello {display_name},\n\n"
                f"We have received your complaint (ID: {complaint_obj.id}).\n"
                "Our team is currently reviewing the details and will update you once the status changes.\n\n"
                "Thank you for bringing this to our attention.\n"
                "We appreciate your patience and will work to resolve it as quickly as possible.\n\n"
                "Regards,\n"
                "Management Team\n"
            )

            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')

            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, f'Complaint saved but email notification failed: {str(e)}')

        messages.success(request, f'Your Complaint ID #{complaint_obj.id} submitted successfully!')
        return redirect('home')

    # Get user's complaints and categories for the form
    user_complaints = Complaint.objects.filter(user=request.user)
    categories = ComplaintCategory.objects.all()

    profile, _ = StudentProfile.objects.get_or_create(user=request.user, defaults={'division': ''})

    context = {
        'complaints': user_complaints,
        'categories': categories,
        'profile': profile
    }
    return render(request, 'OpeningPage.html', context)


def Admin_Login(request):
    if request.method == 'POST':
        username = request.POST.get('adminUsername')
        password = request.POST.get('adminPassword')

        # Debug: Check if user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, f'User "{username}" does not exist.')
            return render(request, 'AdminLogin.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome {user.username}!')
                return redirect('Admin_Panel')
            else:
                messages.error(request, 'Only Admins can log in here. You need staff or superuser privileges.')
                return render(request, 'AdminLogin.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'AdminLogin.html')

    return render(request, 'AdminLogin.html')


@login_required(login_url='/AdminLogin/')
def Admin_Panel(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login_page')

    # Handle status updates
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        new_status = request.POST.get('new_status')
        admin_response = request.POST.get('admin_response', '')

        try:
            complaint = Complaint.objects.get(id=complaint_id)
            old_status = complaint.status

            complaint.status = new_status
            complaint.admin_response = admin_response
            complaint.action_taken = request.POST.get('action_taken', '')

            # Handle action image upload
            if 'action_image' in request.FILES:
                complaint.action_image = request.FILES['action_image']

            if new_status == 'resolved':
                complaint.resolved_date = timezone.now()

            complaint.save()

            # Log the status update
            ComplaintUpdate.objects.create(
                complaint=complaint,
                updated_by=request.user,
                old_status=old_status,
                new_status=new_status,
                update_message=f"Response: {admin_response} | Action: {complaint.action_taken}"
            )

            # Send email notification to user
            if complaint.user.email:
                subject = f'Update on Your Complaint #{complaint.id}'
                message = f"""Hello {complaint.user.first_name or complaint.user.username},

We would like to inform you that the status of your complaint (ID: {complaint.id}) has been updated.
Current Status: {complaint.get_status_display()}

If you have any further questions or need assistance, feel free to reply to this email.

Thank you for your cooperation.

Regards,
Management Team


"""

                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')

                try:
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [complaint.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    messages.warning(request, f'Status updated but email notification failed: {str(e)}')

                if new_status == 'resolved':
                    resolved_subject = f'Complaint #{complaint.id} Resolved'
                    resolved_at = complaint.resolved_date or timezone.now()
                    resolved_timestamp = timezone.localtime(resolved_at).strftime('%b %d, %Y %H:%M')
                    resolution_notes = admin_response if admin_response else 'No resolution notes were provided.'
                    action_notes = complaint.action_taken if complaint.action_taken else 'No additional actions recorded.'

                    resolved_message = f"""Hello {complaint.user.first_name or complaint.user.username},

Your complaint (ID: {complaint.id}) has been marked as resolved.

We hope the issue was addressed to your satisfaction.
If you believe it is not resolved or requires further attention, you may reopen a new complaint anytime.

Thank you for your trust.

Warm Regards,
Management Team

"""

                    try:
                        send_mail(
                            resolved_subject,
                            resolved_message,
                            from_email,
                            [complaint.user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        messages.warning(request, f'Resolution email could not be sent: {str(e)}')

            messages.success(request, f'Complaint #{complaint_id} status updated to {new_status}')

        except Complaint.DoesNotExist:
            messages.error(request, 'Complaint not found.')

        return redirect('Admin_Panel')

    # Get all complaints with filtering options
    complaints = Complaint.objects.all().select_related('user', 'category').order_by('-complaint_date')

    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        complaints = complaints.filter(
            models.Q(name__icontains=search_query) |
            models.Q(division__icontains=search_query) |
            models.Q(complaint__icontains=search_query) |
            models.Q(user__username__icontains=search_query)
        )

    # Calculate analytics data
    total_complaints = complaints.count()
    pending_complaints = complaints.filter(status='pending').count()
    in_progress = complaints.filter(status='in_progress').count()
    resolved_complaints = complaints.filter(status='resolved').count()
    rejected_complaints = complaints.filter(status='rejected').count()
    
    # Combine pending and in-progress for the pending card
    pending_plus_in_progress = pending_complaints + in_progress
    
    # Calculate percentages (avoid division by zero)
    pending_percent = (pending_plus_in_progress / total_complaints * 100) if total_complaints > 0 else 0
    resolved_percent = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    rejected_percent = (rejected_complaints / total_complaints * 100) if total_complaints > 0 else 0

    context = {
        'complaints': complaints,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'current_status_filter': status_filter,
        'current_search': search_query,
        # Analytics data
        'total_complaints': total_complaints,
        'pending_complaints': pending_plus_in_progress,  # Combined pending + in-progress
        'in_progress': in_progress,  # Still pass in_progress separately for display
        'resolved_complaints': resolved_complaints,
        'rejected_complaints': rejected_complaints,
        'pending_percent': pending_percent,
        'resolved_percent': resolved_percent,
        'rejected_percent': rejected_percent,
    }

    return render(request, 'AdminPanel.html', context)


@login_required(login_url='/AdminLogin/')
def download_complaints_pdf(request):
    """Generate and download complaints as PDF"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login_page')

    if not PDF_AVAILABLE:
        messages.error(request, 'PDF generation is not available. Please install reportlab.')
        return redirect('Admin_Panel')

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="complaints_report.pdf"'

    # Fetch complaints from Django ORM (instead of direct MySQL)
    complaints = Complaint.objects.all().select_related('user', 'category').order_by('-complaint_date')

    # Apply same filters as admin panel
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    search_query = request.GET.get('search')
    if search_query:
        complaints = complaints.filter(
            models.Q(name__icontains=search_query) |
            models.Q(division__icontains=search_query) |
            models.Q(complaint__icontains=search_query) |
            models.Q(user__username__icontains=search_query)
        )

    # Add table header
    data = [["ID", "User", "Name", "Division", "Complaint", "Date & Time", "Status", "Priority"]]

    # Helper function for wrapping long text
    def wrap_text(text, width=30):
        if not text:
            return ""
        return "\n".join(textwrap.wrap(str(text), width))

    # Add complaint data
    for complaint in complaints:
        wrapped_row = [
            str(complaint.id),
            complaint.user.username,
            wrap_text(complaint.name, 25),
            wrap_text(complaint.division, 20),
            wrap_text(complaint.complaint, 25),  # complaint wrapped
            complaint.complaint_date.strftime('%Y-%m-%d %H:%M'),
            complaint.get_status_display(),
            complaint.get_priority_display()
        ]
        data.append(wrapped_row)

    # Create PDF using response as file
    pdf = SimpleDocTemplate(response, pagesize=letter)
    table = Table(data, repeatRows=1, colWidths=[30, 60, 70, 60, 120, 80, 60, 50])  # repeat header on new pages

    # Add style to the table
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.cyan),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])

    table.setStyle(style)

    # Build the PDF
    pdf.build([table])

    return response


@login_required(login_url='/')
def view_complaint(request, complaint_id):
    """View full complaint details"""
    try:
        # Allow admins to view any complaint, regular users only their own
        if request.user.is_staff or request.user.is_superuser:
            complaint = Complaint.objects.get(id=complaint_id)
        else:
            complaint = Complaint.objects.get(id=complaint_id, user=request.user)
        return render(request, 'view.html', {'complaint': complaint})
    except Complaint.DoesNotExist:
        messages.error(request, 'Complaint not found or access denied.')
        return redirect('home')


@login_required(login_url='/')
def edit_complaint(request, complaint_id):
    """Edit user's own complaint"""
    try:
        complaint = Complaint.objects.get(id=complaint_id, user=request.user)

        # Only allow editing if complaint is still pending
        if complaint.status != 'pending':
            messages.error(request, 'You can only edit pending complaints.')
            return redirect('home')

        if request.method == 'POST':
            # Update complaint fields
            profile, _ = StudentProfile.objects.get_or_create(user=request.user, defaults={'division': ''})
            complaint.name = (request.user.first_name or '').strip() or request.user.username
            if profile.division:
                complaint.division = profile.division
            complaint.complaint = request.POST.get('complaint')
            complaint.priority = request.POST.get('priority', 'medium')

            # Handle category
            category_id = request.POST.get('category')
            if category_id:
                try:
                    complaint.category = ComplaintCategory.objects.get(id=category_id)
                except ComplaintCategory.DoesNotExist:
                    complaint.category = None
            else:
                complaint.category = None

            # Handle file upload
            new_file = request.FILES.get('complaint_img')
            if new_file:
                complaint.complaint_img = new_file

            complaint.save()
            messages.success(request, f'Complaint #{complaint_id} updated successfully!')
            return redirect('home')

        categories = ComplaintCategory.objects.all()
        profile, _ = StudentProfile.objects.get_or_create(user=request.user, defaults={'division': ''})
        context = {
            'complaint': complaint,
            'categories': categories,
            'profile': profile
        }
        return render(request, 'edit.html', context)

    except Complaint.DoesNotExist:
        messages.error(request, 'Complaint not found or access denied.')
        return redirect('home')


@login_required(login_url='/')
def delete_complaint(request, complaint_id):
    """Delete user's own complaint"""
    try:
        complaint = Complaint.objects.get(id=complaint_id, user=request.user)

        # Only allow deletion if complaint is still pending
        if complaint.status != 'pending':
            messages.error(request, 'You can only delete pending complaints.')
            return redirect('home')

        if request.method == 'POST':
            complaint_id_for_msg = complaint.id
            complaint.delete()
            messages.success(request, f'Complaint #{complaint_id_for_msg} deleted successfully!')
            return redirect('home')

        return render(request, 'delete_confirm.html', {'complaint': complaint})

    except Complaint.DoesNotExist:
        messages.error(request, 'Complaint not found or access denied.')
        return redirect('home')
