# support/views.py

from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages as flash
from django import forms
from profiles.models import Profile, Report, Block
from messaging.models import Message
from django.db.models import Q


def support_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or getattr(request.user.profile, 'is_support', False)):
            return render(request, 'support/denied.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


class ReportResolutionForm(forms.Form):
    ACTION_CHOICES = [
        ('resolved', 'Resolved — Action Taken'),
        ('dismissed', 'Dismissed — No Violation'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add notes about the decision...'}),
        required=False,
        label='Resolution Notes',
    )


class SupportPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


@support_required
def dashboard(request):
    pending_reports = Report.objects.filter(status='pending').count()
    total_users = User.objects.count()
    recent_reports = Report.objects.order_by('-created_at')[:5].select_related('reporter', 'reported')
    inactive_users = User.objects.filter(is_active=False).count()

    return render(request, 'support/dashboard.html', {
        'pending_reports': pending_reports,
        'total_users': total_users,
        'recent_reports': recent_reports,
        'inactive_users': inactive_users,
    })


@support_required
def report_list(request):
    status_filter = request.GET.get('status', 'pending')
    reports = Report.objects.select_related(
        'reporter', 'reported', 'resolved_by'
    ).order_by('-created_at')

    if status_filter in ('pending', 'resolved', 'dismissed'):
        reports = reports.filter(status=status_filter)

    return render(request, 'support/reports.html', {
        'reports': reports,
        'status_filter': status_filter,
    })


@support_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST' and report.status == 'pending':
        form = ReportResolutionForm(request.POST)
        if form.is_valid():
            report.status = form.cleaned_data['action']
            report.resolution_notes = form.cleaned_data['resolution_notes']
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
            report.save()
            flash.success(request, f"Report marked as {report.get_status_display()}.")
            return redirect('support:report_list')
    else:
        form = ReportResolutionForm()

    reporter_reports = Report.objects.filter(reporter=report.reporter).exclude(id=report.id).count()
    reported_reports = Report.objects.filter(reported=report.reported).count()

    return render(request, 'support/report_detail.html', {
        'report': report,
        'form': form,
        'reporter_reports': reporter_reports,
        'reported_reports': reported_reports,
    })


@support_required
def user_list(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.select_related('profile').order_by('username')
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(email__icontains=q) |
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    return render(request, 'support/users.html', {'users': users, 'q': q})


@support_required
def user_detail(request, username):
    target = get_object_or_404(User, username=username)
    reports_received = Report.objects.filter(reported=target).order_by('-created_at')
    reports_made = Report.objects.filter(reporter=target).order_by('-created_at')
    pw_form = SupportPasswordForm()

    return render(request, 'support/user_detail.html', {
        'target': target,
        'reports_received': reports_received,
        'reports_made': reports_made,
        'pw_form': pw_form,
    })


@support_required
def change_password(request, username):
    if request.method != 'POST':
        return redirect('support:user_detail', username=username)
    target = get_object_or_404(User, username=username)
    form = SupportPasswordForm(request.POST)
    if form.is_valid():
        target.set_password(form.cleaned_data['new_password'])
        target.save()
        flash.success(request, f"Password updated for {target.username}.")
    else:
        for error in form.errors.values():
            flash.error(request, error.as_text())
    return redirect('support:user_detail', username=username)


@support_required
def toggle_active(request, username):
    if request.method != 'POST':
        return redirect('support:user_detail', username=username)
    target = get_object_or_404(User, username=username)
    if target == request.user:
        flash.error(request, "You cannot deactivate your own account.")
        return redirect('support:user_detail', username=username)
    target.is_active = not target.is_active
    target.save()
    status = "reactivated" if target.is_active else "deactivated"
    flash.success(request, f"{target.username} has been {status}.")
    return redirect('support:user_detail', username=username)


@support_required
def toggle_support(request, username):
    if request.method != 'POST':
        return redirect('support:user_detail', username=username)
    target = get_object_or_404(User, username=username)
    target.profile.is_support = not target.profile.is_support
    target.profile.save(update_fields=['is_support'])
    status = "granted" if target.profile.is_support else "removed"
    flash.success(request, f"Support access {status} for {target.username}.")
    return redirect('support:user_detail', username=username)
