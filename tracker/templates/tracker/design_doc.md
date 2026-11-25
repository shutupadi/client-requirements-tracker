{% autoescape off %}# Technical Design Document: {{ project.name }}

Client: {{ project.client_name }}
Methodology: {{ project.get_methodology_display }}
Version: v{{ version }}

## 1. Background
{{ project.description|default:"No description provided." }}

## 2. Functional Requirements
{% for r in functional %}- {{ r.code }} {{ r.title }} [{{ r.get_priority_display }}]
  {{ r.description }}
{% empty %}- None captured.
{% endfor %}
## 3. Non-Functional Requirements
{% for r in non_functional %}- {{ r.code }} {{ r.title }} [{{ r.get_priority_display }}]
  {{ r.description }}
{% empty %}- None captured.
{% endfor %}
## 4. Proposed Technical Design
Architecture: Django web application (MVC-style: models, views, templates) on a PostgreSQL database, hosted on Azure App Service.

Modules (one per functional requirement):
{% for r in functional %}- Module {{ forloop.counter }}: {{ r.title }} (implements {{ r.code }})
{% empty %}- None.
{% endfor %}
## 5. Implementation Plan ({{ project.iteration_label }}s)
{% for it in iterations %}### {{ it.name }} ({{ it.start_date }} to {{ it.end_date }})
{% for r in it.requirements.all %}- {{ r.code }} {{ r.title }}: {{ plan_steps|join:" -> " }}
{% empty %}- No requirements planned.
{% endfor %}
{% empty %}No {{ project.iteration_label|lower }}s defined yet.
{% endfor %}{% if unplanned %}### Not yet planned
{% for r in unplanned %}- {{ r.code }} {{ r.title }}
{% endfor %}{% endif %}
## 6. Testing Approach
- Unit tests with pytest for every module.
- System Integration Testing (SIT): one end-to-end case per requirement.
- Client review and sign-off on each document version.

## 7. Sign-off
Pending client review.
{% endautoescape %}
