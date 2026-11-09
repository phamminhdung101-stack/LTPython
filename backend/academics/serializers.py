from rest_framework import serializers
from .models import Department, Class, Subject


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_id', 'department_name']


class ClassSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Class
        fields = ['class_id', 'class_name', 'department', 'department_id', 'is_locked']


class SubjectSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name', 'department', 'department_id']

