"""Unit tests: model rules."""
import pytest
from django.db import IntegrityError

from tracker.models import Project, Requirement


def test_iteration_label_depends_on_methodology(db):
    assert Project(methodology=Project.Methodology.AGILE).iteration_label == "Sprint"
    assert Project(methodology=Project.Methodology.WATERFALL).iteration_label == "Milestone"


def test_progress_percent(project, requirement):
    assert project.progress_percent() == 0
    Requirement.objects.create(project=project, code="REQ-002", title="B", description="b",
                               status=Requirement.Status.DONE)
    assert project.progress_percent() == 50


def test_progress_is_zero_with_no_requirements(project):
    assert project.progress_percent() == 0


def test_requirement_code_unique_per_project(project, requirement):
    with pytest.raises(IntegrityError):
        Requirement.objects.create(project=project, code="REQ-001", title="Dup", description="x")
