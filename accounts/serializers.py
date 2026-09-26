"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

Student = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'college_name',
            'university', 'regulation', 'branch',
            'current_year', 'current_semester',
            'study_streak', 'profile_completed', 'created_at'
        ]
        read_only_fields = ['id', 'study_streak', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Student
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return Student.objects.create_user(**validated_data)
