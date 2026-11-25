"""
Data model (normalised relational schema).

    Project ──< Requirement >── Iteration (sprint or milestone)
       │
       ├──< Iteration
       │
       └──< DesignDocument ──< SignOff

- A Project belongs to a client and follows Agile OR Waterfall.
- Requirements are captured per project and planned into an Iteration.
- An Iteration is a Sprint (Agile) or a Milestone (Waterfall).
- A DesignDocument is auto-generated from the requirements. Every
  regeneration creates a NEW version, so old versions are never lost.
- A SignOff is a client review decision on one document version.
"""
from django.db import models


class Project(models.Model):
    class Methodology(models.TextChoices):
        AGILE = "AGILE", "Agile"
        WATERFALL = "WATERFALL", "Waterfall"

    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    methodology = models.CharField(max_length=10, choices=Methodology.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.client_name})"

    @property
    def iteration_label(self):
        """Agile projects plan work in sprints, Waterfall in milestones."""
        return "Sprint" if self.methodology == self.Methodology.AGILE else "Milestone"

    def latest_document(self):
        return self.documents.order_by("-version").first()

    def progress_percent(self):
        total = self.requirements.count()
        if total == 0:
            return 0
        done = self.requirements.filter(status=Requirement.Status.DONE).count()
        return round(done * 100 / total)


class Iteration(models.Model):
    """A Sprint (Agile) or a Milestone (Waterfall)."""

    class Kind(models.TextChoices):
        SPRINT = "SPRINT", "Sprint"
        MILESTONE = "MILESTONE", "Milestone"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="iterations")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class Requirement(models.Model):
    class Priority(models.TextChoices):
        MUST = "MUST", "Must have"
        SHOULD = "SHOULD", "Should have"
        COULD = "COULD", "Could have"

    class Type(models.TextChoices):
        FUNCTIONAL = "FUNCTIONAL", "Functional"
        NON_FUNCTIONAL = "NON_FUNCTIONAL", "Non-functional"

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        DONE = "DONE", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")
    iteration = models.ForeignKey(
        Iteration, on_delete=models.SET_NULL, null=True, blank=True, related_name="requirements"
    )
    code = models.CharField(max_length=20, help_text="e.g. REQ-001")
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirement_type = models.CharField(max_length=20, choices=Type.choices, default=Type.FUNCTIONAL)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MUST)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    stakeholder = models.CharField(max_length=100, blank=True, help_text="Who asked for it")

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="unique_requirement_code_per_project")
        ]

    def __str__(self):
        return f"{self.code}: {self.title}"


class DesignDocument(models.Model):
    """A versioned technical design doc + implementation plan."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        APPROVED = "APPROVED", "Approved"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes requested"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    version = models.PositiveIntegerField()
    content = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version"]
        constraints = [
            models.UniqueConstraint(fields=["project", "version"], name="unique_version_per_project")
        ]

    def __str__(self):
        return f"{self.project.name} design v{self.version}"


class SignOff(models.Model):
    """A client review decision on one document version."""

    class Decision(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes requested"

    document = models.ForeignKey(DesignDocument, on_delete=models.CASCADE, related_name="signoffs")
    reviewer_name = models.CharField(max_length=100)
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comments = models.TextField(blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer_name}: {self.get_decision_display()} on v{self.document.version}"
