from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Department, Class, Subject
from .serializers import DepartmentSerializer, ClassSerializer, SubjectSerializer


class DepartmentListAPIView(APIView):
    """
    GET /api/departments/
    Danh sách các khoa / đơn vị đào tạo
    """
    permission_classes = [AllowAny]

    def get(self, request):
        depts = Department.objects.all().order_by('department_id')
        serializer = DepartmentSerializer(depts, many=True)
        return Response({
            'status': 'success',
            'total': depts.count(),
            'departments': serializer.data,
        }, status=status.HTTP_200_OK)


class ClassListAPIView(APIView):
    """
    GET /api/classes/
    Danh sách các lớp học, có hỗ trợ lọc theo khoa (?department_id=...)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Class.objects.select_related('department').all().order_by('class_id')
        dept_id = request.GET.get('department_id')
        if dept_id and dept_id.isdigit():
            qs = qs.filter(department_id=int(dept_id))

        serializer = ClassSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'classes': serializer.data,
        }, status=status.HTTP_200_OK)


class SubjectListAPIView(APIView):
    """
    GET /api/subjects/
    Danh sách môn học, hỗ trợ lọc theo khoa (?department_id=...) và tìm kiếm (?q=...)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Subject.objects.select_related('department').all().order_by('subject_id')
        dept_id = request.GET.get('department_id')
        q = request.GET.get('q', '').strip()

        if dept_id and dept_id.isdigit():
            qs = qs.filter(department_id=int(dept_id))
        if q:
            qs = qs.filter(subject_name__icontains=q)

        serializer = SubjectSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'subjects': serializer.data,
        }, status=status.HTTP_200_OK)

