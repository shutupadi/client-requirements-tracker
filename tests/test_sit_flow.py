"""
SIT (System Integration Test): runs the full business flow through the
real URLs, views, forms, services and database together.
Matches SIT-01 to SIT-05 in docs/SIT_test_cases.md.
"""
import pytest
from django.urls import reverse

from tracker.models import DesignDocument, Iteration, Project


@pytest.mark.django_db
def test_end_to_end_requirement_to_signoff(client):
    # SIT-01: create a client project
    resp = client.post(reverse("project_list"), {
        "name": "Sales Dashboard", "client_name": "Pharma Co", "description": "Rep dashboard", "methodology": "AGILE",
    })
    project = Project.objects.get(name="Sales Dashboard")
    assert resp.status_code == 302

    # SIT-02: add a sprint (kind is set automatically from methodology)
    client.post(reverse("add_iteration", args=[project.pk]),
                {"name": "Sprint 1", "start_date": "2026-12-01", "end_date": "2026-12-14"})
    sprint = project.iterations.get()
    assert sprint.kind == Iteration.Kind.SPRINT

    # SIT-03: capture a requirement planned into the sprint
    client.post(reverse("add_requirement", args=[project.pk]), {
        "code": "REQ-001", "title": "Territory view", "description": "Show sales by territory",
        "requirement_type": "FUNCTIONAL", "priority": "MUST", "status": "NEW", "stakeholder": "Ops", "iteration": sprint.pk,
    })
    assert project.requirements.count() == 1

    # SIT-04: generate design doc + implementation plan
    resp = client.post(reverse("generate_document", args=[project.pk]))
    doc = project.documents.get()
    assert resp.status_code == 302
    assert "Territory view" in client.get(reverse("document_detail", args=[doc.pk])).content.decode()

    # SIT-05: client requests changes, team regenerates v2, client approves v2
    client.post(reverse("document_detail", args=[doc.pk]),
                {"reviewer_name": "Client PM", "decision": "CHANGES_REQUESTED", "comments": "Add export"})
    doc.refresh_from_db()
    assert doc.status == DesignDocument.Status.CHANGES_REQUESTED

    client.post(reverse("generate_document", args=[project.pk]))
    v2 = project.latest_document()
    client.post(reverse("document_detail", args=[v2.pk]),
                {"reviewer_name": "Client PM", "decision": "APPROVED", "comments": ""})
    v2.refresh_from_db()
    assert v2.version == 2 and v2.status == DesignDocument.Status.APPROVED


@pytest.mark.django_db
def test_invalid_iteration_dates_are_rejected(client, project):
    resp = client.post(reverse("add_iteration", args=[project.pk]),
                       {"name": "Bad", "start_date": "2026-12-14", "end_date": "2026-12-01"})
    assert resp.status_code == 200  # form re-shown with error
    assert project.iterations.count() == 0


@pytest.mark.django_db
def test_duplicate_requirement_code_shows_error(client, requirement):
    resp = client.post(reverse("add_requirement", args=[requirement.project.pk]), {
        "code": "REQ-001", "title": "Dup", "description": "x",
        "requirement_type": "FUNCTIONAL", "priority": "MUST", "status": "NEW",
    })
    assert resp.status_code == 200
    assert "already exists" in resp.content.decode()
