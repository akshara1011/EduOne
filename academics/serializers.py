"""Serializers for academic models."""
from rest_framework import serializers
from .models import University, Regulation, Branch, Semester, Subject, Unit, Topic


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'short_name', 'state', 'website']


class RegulationSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.short_name', read_only=True)

    class Meta:
        model = Regulation
        fields = ['id', 'name', 'year', 'university', 'university_name']


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'short_name']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'semester_number', 'year_of_study', 'regulation', 'branch']


class SubjectSerializer(serializers.ModelSerializer):
    unit_count = serializers.IntegerField(source='units.count', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'subject_code', 'credits', 'subject_type', 'unit_count']


class UnitSerializer(serializers.ModelSerializer):
    topic_count = serializers.IntegerField(source='topics.count', read_only=True)

    class Meta:
        model = Unit
        fields = ['id', 'unit_number', 'name', 'subject', 'topic_count']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'unit', 'order', 'description']
