"""Unit tests: document generation and sign-off logic."""
import pytest

from tracker.models import DesignDocument, SignOff
from tracker.services import generate_design_document, record_signoff


def test_generate_requires_requirements(project):
    with pytest.raises(ValueError):
        generate_design_document(project)


def test_generated_doc_contains_requirements_and_plan(requirement):
    doc = generate_design_document(requirement.project)
    assert doc.version == 1
    assert doc.status == DesignDocument.Status.DRAFT
    assert "REQ-001 User login" in doc.content
    assert "Sprint 1" in doc.content
    assert "Implementation Plan (Sprints)" in doc.content


def test_regenerating_creates_new_version(requirement):
    v1 = generate_design_document(requirement.project)
    v2 = generate_design_document(requirement.project)
    assert (v1.version, v2.version) == (1, 2)
    assert requirement.project.documents.count() == 2  # old version is kept


def test_signoff_updates_document_status(requirement):
    doc = generate_design_document(requirement.project)
    record_signoff(doc, "Client PM", SignOff.Decision.APPROVED, "Looks good")
    doc.refresh_from_db()
    assert doc.status == DesignDocument.Status.APPROVED
    assert doc.signoffs.count() == 1


def test_cannot_sign_off_old_version(requirement):
    v1 = generate_design_document(requirement.project)
    generate_design_document(requirement.project)
    with pytest.raises(ValueError):
        record_signoff(v1, "Client PM", SignOff.Decision.APPROVED)
