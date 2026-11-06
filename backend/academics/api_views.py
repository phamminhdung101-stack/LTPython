from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Department, Class, Subject
from .serializers import DepartmentSerializer, ClassSerializer, SubjectSerializer
from permissions.rest_permissions import IsAdminUserRole, IsAuthenticatedCustom


class DepartmentListAPIView(APIView):
    """
    GET /api/departments/
    Danh sách các khoa / đơn vị đào tạo
    POST /api/departments/
    Thêm khoa mới (chỉ Admin)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request):
        depts = Department.objects.all().order_by('department_id')
        serializer = DepartmentSerializer(depts, many=True)
        return Response({
            'status': 'success',
            'total': depts.count(),
            'departments': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        dept = serializer.save()
        return Response({
            'status': 'success',
            'message': f'Đã thêm khoa "{dept.department_name}" thành công.',
            'department': DepartmentSerializer(dept).data,
        }, status=status.HTTP_201_CREATED)


class DepartmentDetailAPIView(APIView):
    """
    GET /api/departments/<pk>/
    PUT/PATCH /api/departments/<pk>/
    DELETE /api/departments/<pk>/
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request, pk):
        try:
            dept = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy khoa.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'success', 'department': DepartmentSerializer(dept).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            dept = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy khoa.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        dept = serializer.save()
        return Response({'status': 'success', 'department': DepartmentSerializer(dept).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            dept = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy khoa.'}, status=status.HTTP_404_NOT_FOUND)
        name = dept.department_name
        dept.delete()
        return Response({'status': 'success', 'message': f'Đã xóa khoa "{name}" thành công.'}, status=status.HTTP_200_OK)


class ClassListAPIView(APIView):
    """
    GET /api/classes/
    Danh sách các lớp học, có hỗ trợ lọc theo khoa (?department_id=...)
    POST /api/classes/
    Thêm lớp mới (chỉ Admin)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request):
        qs = Class.objects.select_related('department').all().order_by('class_id')
        dept_id = request.GET.get('department_id')
        if dept_id and str(dept_id).isdigit():
            qs = qs.filter(department_id=int(dept_id))

        serializer = ClassSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'classes': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        cls = serializer.save()
        return Response({
            'status': 'success',
            'message': f'Đã tạo lớp "{cls.class_name}" thành công.',
            'class': ClassSerializer(cls).data,
        }, status=status.HTTP_201_CREATED)


class ClassDetailAPIView(APIView):
    """
    GET /api/classes/<pk>/
    PUT/PATCH /api/classes/<pk>/
    DELETE /api/classes/<pk>/
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request, pk):
        try:
            cls = Class.objects.select_related('department').get(pk=pk)
        except Class.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy lớp.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'success', 'class': ClassSerializer(cls).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            cls = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy lớp.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClassSerializer(cls, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        cls = serializer.save()
        return Response({'status': 'success', 'class': ClassSerializer(cls).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            cls = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy lớp.'}, status=status.HTTP_404_NOT_FOUND)
        name = cls.class_name
        cls.delete()
        return Response({'status': 'success', 'message': f'Đã xóa lớp "{name}" thành công.'}, status=status.HTTP_200_OK)


class SubjectListAPIView(APIView):
    """
    GET /api/subjects/
    Danh sách môn học, hỗ trợ lọc theo khoa (?department_id=...) và tìm kiếm (?q=...)
    POST /api/subjects/
    Thêm môn học mới (chỉ Admin)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request):
        qs = Subject.objects.select_related('department').all().order_by('subject_id')
        dept_id = request.GET.get('department_id')
        q = request.GET.get('q', '').strip()

        if dept_id and str(dept_id).isdigit():
            qs = qs.filter(department_id=int(dept_id))
        if q:
            qs = qs.filter(subject_name__icontains=q)

        serializer = SubjectSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'subjects': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        subj = serializer.save()
        return Response({
            'status': 'success',
            'message': f'Đã tạo môn học "{subj.subject_name}" thành công.',
            'subject': SubjectSerializer(subj).data,
        }, status=status.HTTP_201_CREATED)


class SubjectDetailAPIView(APIView):
    """
    GET /api/subjects/<pk>/
    PUT/PATCH /api/subjects/<pk>/
    DELETE /api/subjects/<pk>/
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserRole()]
        return [AllowAny()]

    def get(self, request, pk):
        try:
            subj = Subject.objects.select_related('department').get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy môn học.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'success', 'subject': SubjectSerializer(subj).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            subj = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy môn học.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubjectSerializer(subj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        subj = serializer.save()
        return Response({'status': 'success', 'subject': SubjectSerializer(subj).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            subj = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy môn học.'}, status=status.HTTP_404_NOT_FOUND)
        name = subj.subject_name
        subj.delete()
        return Response({'status': 'success', 'message': f'Đã xóa môn học "{name}" thành công.'}, status=status.HTTP_200_OK)
