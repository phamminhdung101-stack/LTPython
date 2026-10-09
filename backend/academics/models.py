from django.db import models


class Department(models.Model):
    """Khoa / Faculty"""
    department_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Khoa'
        verbose_name_plural = 'Khoa'
        ordering = ['department_name']

    def __str__(self):
        return self.department_name


class Class(models.Model):
    """Lớp / Khóa học"""
    class_name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='classes',
    )
    is_locked = models.BooleanField(default=False)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Lớp'
        verbose_name_plural = 'Lớp'
        ordering = ['class_name']

    def __str__(self):
        return self.class_name


class Subject(models.Model):
    """Môn học"""
    subject_name = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subjects',
    )

    class Meta:
        db_table = 'subjects'
        verbose_name = 'Môn học'
        verbose_name_plural = 'Môn học'
        unique_together = [('subject_name', 'department')]
        ordering = ['subject_name']

    def __str__(self):
        return self.subject_name
