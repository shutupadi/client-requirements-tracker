"""
Business logic, kept out of the views so it is easy to unit test.

1. generate_design_document(): turns a project's requirements into a
   technical design doc + implementation plan, using a Django template.
   No AI is involved: it is rule-based text generation.
2. record_signoff(): stores a client review decision and updates the
   document's status.
"""
from django.db import transaction
from django.template.loader import render_to_string

from .models import DesignDocument, Project, Requirement, SignOff

# Simple rule: every requirement becomes one module in the design,
# and the implementation plan has these standard steps per module.
PLAN_STEPS = ["Design", "Build", "Unit test (pytest)", "SIT", "Client review"]


@transaction.atomic
def generate_design_document(project: Project) -> DesignDocument:
    requirements = list(project.requirements.select_related("iteration"))
    if not requirements:
        raise ValueError("Add at least one requirement before generating a design document.")

    last = project.documents.order_by("-version").first()
    next_version = (last.version + 1) if last else 1

    content = render_to_string(
        "tracker/design_doc.md",
        {
            "project": project,
            "version": next_version,
            "functional": [r for r in requirements if r.requirement_type == Requirement.Type.FUNCTIONAL],
            "non_functional": [r for r in requirements if r.requirement_type == Requirement.Type.NON_FUNCTIONAL],
            "iterations": project.iterations.prefetch_related("requirements"),
            "unplanned": [r for r in requirements if r.iteration is None],
            "plan_steps": PLAN_STEPS,
        },
    )
    return DesignDocument.objects.create(project=project, version=next_version, content=content)


@transaction.atomic
def record_signoff(document: DesignDocument, reviewer_name: str, decision: str, comments: str = "") -> SignOff:
    latest = document.project.latest_document()
    if latest and document.pk != latest.pk:
        raise ValueError("Only the latest version of a document can be signed off.")

    signoff = SignOff.objects.create(
        document=document, reviewer_name=reviewer_name, decision=decision, comments=comments
    )
    document.status = decision  # APPROVED or CHANGES_REQUESTED
    document.save(update_fields=["status"])
    return signoff
