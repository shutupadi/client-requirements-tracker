from django.contrib import admin

from .models import DesignDocument, Iteration, Project, Requirement, SignOff

admin.site.register(Project)
admin.site.register(Iteration)
admin.site.register(DesignDocument)
admin.site.register(SignOff)


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "project", "priority", "status", "iteration"]
    list_filter = ["project", "status", "priority"]
