from django.urls import path

from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/requirements/add/", views.add_requirement, name="add_requirement"),
    path("projects/<int:pk>/iterations/add/", views.add_iteration, name="add_iteration"),
    path("projects/<int:pk>/generate/", views.generate_document, name="generate_document"),
    path("requirements/<int:pk>/edit/", views.edit_requirement, name="edit_requirement"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
]
