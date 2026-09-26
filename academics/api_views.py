"""
REST API views for academic hierarchy.
"""
from rest_framework import generics, permissions
from .models import University, Regulation, Branch, Semester, Subject, Unit, Topic
from .serializers import (
    UniversitySerializer, RegulationSerializer, BranchSerializer,
    SemesterSerializer, SubjectSerializer, UnitSerializer, TopicSerializer
)


class UniversityListView(generics.ListAPIView):
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny]


class RegulationListView(generics.ListAPIView):
    serializer_class = RegulationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Regulation.objects.filter(is_active=True)
        university_id = self.request.query_params.get('university_id')
        if university_id:
            qs = qs.filter(university_id=university_id)
        return qs


class BranchListView(generics.ListAPIView):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [permissions.AllowAny]


class SemesterListView(generics.ListAPIView):
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Semester.objects.all()
        regulation_id = self.request.query_params.get('regulation_id')
        branch_id = self.request.query_params.get('branch_id')
        if regulation_id:
            qs = qs.filter(regulation_id=regulation_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs


class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Subject.objects.filter(is_active=True)
        semester_id = self.request.query_params.get('semester_id')
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        return qs


class UnitListView(generics.ListAPIView):
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Unit.objects.all()
        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


class TopicListView(generics.ListAPIView):
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Topic.objects.all()
        unit_id = self.request.query_params.get('unit_id')
        if unit_id:
            qs = qs.filter(unit_id=unit_id)
        return qs
