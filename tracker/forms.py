from django import forms

from .models import Iteration, Project, Requirement, SignOff


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "client_name", "description", "methodology"]


class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ["code", "title", "description", "requirement_type", "priority", "status", "stakeholder", "iteration"]

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        # Only show sprints/milestones that belong to this project
        self.fields["iteration"].queryset = Iteration.objects.filter(project=project)

    def clean_code(self):
        code = self.cleaned_data["code"]
        qs = Requirement.objects.filter(project=self.project, code=code).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This requirement code already exists in the project.")
        return code


class IterationForm(forms.ModelForm):
    class Meta:
        model = Iteration
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        data = super().clean()
        if data.get("start_date") and data.get("end_date") and data["end_date"] < data["start_date"]:
            raise forms.ValidationError("End date must be after start date.")
        return data


class SignOffForm(forms.ModelForm):
    class Meta:
        model = SignOff
        fields = ["reviewer_name", "decision", "comments"]
