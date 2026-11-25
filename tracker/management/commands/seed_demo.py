"""Load demo data: python manage.py seed_demo"""
from datetime import date

from django.core.management.base import BaseCommand

from tracker.models import Iteration, Project, Requirement


class Command(BaseCommand):
    help = "Create two demo client projects (one Agile, one Waterfall)."

    def handle(self, *args, **options):
        agile, _ = Project.objects.get_or_create(
            name="Sales Rep Dashboard",
            defaults={
                "client_name": "Pharma Co",
                "methodology": Project.Methodology.AGILE,
                "description": "Dashboard for sales reps to track prescriptions and call plans by territory.",
            },
        )
        s1, _ = Iteration.objects.get_or_create(
            project=agile, name="Sprint 1",
            defaults={"kind": Iteration.Kind.SPRINT, "start_date": date(2026, 12, 1), "end_date": date(2026, 12, 14)},
        )
        s2, _ = Iteration.objects.get_or_create(
            project=agile, name="Sprint 2",
            defaults={"kind": Iteration.Kind.SPRINT, "start_date": date(2026, 12, 15), "end_date": date(2026, 12, 28)},
        )
        reqs = [
            ("REQ-001", "Login for sales reps", "Reps log in with company email.", "FUNCTIONAL", "MUST", "DONE", s1),
            ("REQ-002", "Territory sales view", "Show weekly prescriptions per territory.", "FUNCTIONAL", "MUST", "IN_PROGRESS", s1),
            ("REQ-003", "Export to Excel", "Download the territory table as Excel.", "FUNCTIONAL", "SHOULD", "NEW", s2),
            ("REQ-004", "Page load under 3 seconds", "Dashboard loads in under 3s for 200 users.", "NON_FUNCTIONAL", "MUST", "NEW", s2),
        ]
        for code, title, desc, rtype, prio, status, it in reqs:
            Requirement.objects.get_or_create(
                project=agile, code=code,
                defaults=dict(title=title, description=desc, requirement_type=rtype, priority=prio,
                              status=status, iteration=it, stakeholder="Sales Ops Lead"),
            )

        wf, _ = Project.objects.get_or_create(
            name="Data Warehouse Migration",
            defaults={
                "client_name": "Retail Co",
                "methodology": Project.Methodology.WATERFALL,
                "description": "Move legacy SQL Server reporting tables to a cloud PostgreSQL warehouse.",
            },
        )
        m1, _ = Iteration.objects.get_or_create(
            project=wf, name="M1: Requirements & Design",
            defaults={"kind": Iteration.Kind.MILESTONE, "start_date": date(2026, 12, 1), "end_date": date(2026, 12, 31)},
        )
        Requirement.objects.get_or_create(
            project=wf, code="REQ-001",
            defaults=dict(title="Migrate sales fact table", description="Move sales fact table with history.",
                          iteration=m1, stakeholder="BI Manager"),
        )
        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
