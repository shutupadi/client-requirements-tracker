from datetime import date

import pytest

from tracker.models import Iteration, Project, Requirement


@pytest.fixture
def project(db):
    return Project.objects.create(name="Demo", client_name="Client A", methodology=Project.Methodology.AGILE)


@pytest.fixture
def sprint(project):
    return Iteration.objects.create(
        project=project, kind=Iteration.Kind.SPRINT, name="Sprint 1",
        start_date=date(2026, 12, 1), end_date=date(2026, 12, 14),
    )


@pytest.fixture
def requirement(project, sprint):
    return Requirement.objects.create(
        project=project, iteration=sprint, code="REQ-001", title="User login", description="Users can log in."
    )
