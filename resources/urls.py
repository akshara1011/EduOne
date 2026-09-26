from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [
    # Resources home
    path("", views.resources_home, name="home"),

    # Notes
    path("notes/", views.notes, name="notes"),

    # Download note
    path(
        "notes/<int:note_id>/download/",
        views.download_note,
        name="download_note",
    ),

    # Videos
    path("videos/", views.videos, name="videos"),
]