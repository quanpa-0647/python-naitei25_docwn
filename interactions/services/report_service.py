# interactions/services/report_service.py
from interactions.models import Report
from django.utils.translation import gettext_lazy as _

class ReportService:
    @staticmethod
    def create_report(user, comment, cleaned_data):
        # Chặn báo cáo trùng:
        if Report.objects.filter(user=user, comment=comment).exists():
            return None, _("Bạn đã báo cáo bình luận này rồi.")

        report = Report.objects.create(
            user=user,
            comment=comment,
            reason=cleaned_data.get("reason"),
            description=cleaned_data.get("description", "")
        )
        report.save()
        return report, None
