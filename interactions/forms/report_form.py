# interactions/forms/report_form.py
from django import forms
from interactions.models import Report
from constants import TEXTAREA_ROWS

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "description"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-selectt bg-body text-body"}),
            "description": forms.Textarea(attrs={"class": "form-control bg-body text-body", "rows": TEXTAREA_ROWS}),
        }
