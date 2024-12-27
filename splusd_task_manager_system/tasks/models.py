from django.db import models


# Create your models here.
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    iteration = models.CharField(max_length=100)
    project = models.CharField(max_length=100)
    sub_project = models.CharField(max_length=100)
    team_member = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)
    # 新增字段
    name = models.CharField(max_length=100)  # 新增 Name 字段
    STATUS_CHOICES = [
        ('completed', '完成'),
        ('in_progress', '进行中'),
        ('delay', '延迟'),
        ('plan', '计划'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)  # 新增 Status 字段
    is_reporting_to_me = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.alias
