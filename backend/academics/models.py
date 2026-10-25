from django.db import models


class Department(models.Model):
    """Bảng departments trong PostgreSQL"""
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = False
        db_table = 'departments'
        verbose_name = 'Khoa'
        verbose_name_plural = 'Khoa'
        ordering = ['department_id']

    def __str__(self):
        return self.department_name


class Class(models.Model):
    """Bảng classes trong PostgreSQL"""
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        db_column='department_id',
        related_name='classes',
    )
    is_locked = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'classes'
        verbose_name = 'Lớp'
        verbose_name_plural = 'Lớp'
        ordering = ['class_id']

    def __str__(self):
        return self.class_name


class Subject(models.Model):
    """Bảng subjects trong PostgreSQL"""
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        db_column='department_id',
        related_name='subjects',
    )

    class Meta:
        managed = False
        db_table = 'subjects'
        verbose_name = 'Môn học'
        verbose_name_plural = 'Môn học'
        unique_together = (('subject_name', 'department'),)
        ordering = ['subject_id']

    def __str__(self):
        return self.subject_name
