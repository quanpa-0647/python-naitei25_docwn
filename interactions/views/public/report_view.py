# interactions/views/public/report_view.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from interactions.models import Comment
from interactions.forms.report_form import ReportForm
from interactions.services.report_service import ReportService
from http import HTTPStatus

@require_POST
@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    form = ReportForm(request.POST)
    if form.is_valid():
        report, error = ReportService.create_report(request.user, comment, form.cleaned_data)
        if error:
            return JsonResponse({"success": False, "message": error}, status= HTTPStatus.BAD_REQUEST)

        return JsonResponse({
            "success": True,
            "message": _("Báo cáo đã được gửi."),
            "report_id": report.id,
            "comment_id": comment.id
        })
    else:
        return JsonResponse({
            "success": False,
            "errors": form.errors,
            "message": _("Dữ liệu không hợp lệ.")
        }, status= HTTPStatus.BAD_REQUEST)
