from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IterationForm, ProjectForm, RequirementForm, SignOffForm
from .models import DesignDocument, Iteration, Project, Requirement
from .services import generate_design_document, record_signoff


def project_list(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, "Project created.")
        return redirect("project_detail", pk=project.pk)
    return render(request, "tracker/project_list.html", {"projects": Project.objects.all(), "form": form})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(
        request,
        "tracker/project_detail.html",
        {
            "project": project,
            "requirements": project.requirements.select_related("iteration"),
            "iterations": project.iterations.all(),
            "documents": project.documents.all(),
            "requirement_form": RequirementForm(project=project),
            "iteration_form": IterationForm(),
        },
    )


def add_requirement(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = RequirementForm(request.POST or None, project=project)
    if request.method == "POST" and form.is_valid():
        requirement = form.save(commit=False)
        requirement.project = project
        requirement.save()
        messages.success(request, f"Requirement {requirement.code} added.")
        return redirect("project_detail", pk=project.pk)
    return render(request, "tracker/form.html", {"form": form, "title": "Add requirement", "project": project})


def edit_requirement(request, pk):
    requirement = get_object_or_404(Requirement, pk=pk)
    form = RequirementForm(request.POST or None, instance=requirement, project=requirement.project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Requirement {requirement.code} updated.")
        return redirect("project_detail", pk=requirement.project.pk)
    return render(request, "tracker/form.html", {"form": form, "title": f"Edit {requirement.code}", "project": requirement.project})


def add_iteration(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = IterationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        iteration = form.save(commit=False)
        iteration.project = project
        # Sprint for Agile projects, Milestone for Waterfall projects
        iteration.kind = Iteration.Kind.SPRINT if project.methodology == Project.Methodology.AGILE else Iteration.Kind.MILESTONE
        iteration.save()
        messages.success(request, f"{project.iteration_label} added.")
        return redirect("project_detail", pk=project.pk)
    return render(request, "tracker/form.html", {"form": form, "title": f"Add {project.iteration_label}", "project": project})


def generate_document(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method != "POST":
        return redirect("project_detail", pk=pk)
    try:
        doc = generate_design_document(project)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("project_detail", pk=pk)
    messages.success(request, f"Design document v{doc.version} generated.")
    return redirect("document_detail", pk=doc.pk)


def document_detail(request, pk):
    document = get_object_or_404(DesignDocument, pk=pk)
    form = SignOffForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            record_signoff(document, **form.cleaned_data)
            messages.success(request, "Review recorded.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("document_detail", pk=document.pk)
    return render(
        request,
        "tracker/document_detail.html",
        {
            "document": document,
            "is_latest": document == document.project.latest_document(),
            "signoffs": document.signoffs.all(),
            "form": form,
        },
    )
