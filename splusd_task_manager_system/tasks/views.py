from django.shortcuts import render

# Create your views here.
# tasks/views.py

from django.shortcuts import render, get_object_or_404, redirect

from tasks.utils.common_helper import deal_text
from .forms import UploadExcelForm
from .models import Task
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime, timedelta
from django.http import HttpResponse
import pandas as pd


def upload_excel(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 处理 Excel 文件
                excel_file = request.FILES['file']
                print(excel_file.name)
                # 使用 openpyxl 引擎读取 Excel 文件
                # 读取第一个 sheet 的名称
                df = pd.read_excel(excel_file, engine='openpyxl')
                iteration = '11月25~12月6'  # 固定迭代为 2022Q1
                # 创建一个空列表用于批量插入
                tasks_to_create = []

                # 从第二行开始读取数据
                for index, row in df.iterrows():
                    if index == 0:  # 跳过第一行
                        continue
        
                    project = row[0]  # 第一列
                    sub_project = row[1]  # 第二列
                    team_member = row[2]  # 第三列
                    alias = row[3]  # 第四列
                    is_report = row[14]  # 第15列
                    is_reporting_to_me = (is_report == 'Yes')
                    competed_tasks = deal_text(str(row[5]))
                    ingress_tasks = deal_text(str(row[9]))
                    delayed_tasks = deal_text(str(row[10]))
                    planning_tasks = deal_text(str(row[11]))
                    # 为每个任务状态创建 Task 实例并获取返回值
                    tasks_to_create += __create_tasks(competed_tasks, 'completed', project, sub_project, iteration, team_member, alias, is_reporting_to_me)
                    tasks_to_create += __create_tasks(ingress_tasks, 'in_progress', project, sub_project, iteration, team_member, alias, is_reporting_to_me)
                    tasks_to_create += __create_tasks(delayed_tasks, 'delay', project, sub_project, iteration, team_member, alias, is_reporting_to_me)
                    tasks_to_create += __create_tasks(planning_tasks, 'plan', project, sub_project, iteration, team_member, alias, is_reporting_to_me)

                # 批量插入数据库
                Task.objects.bulk_create(tasks_to_create)
                # 在这里可以处理 DataFrame，例如保存到数据库
                messages.success(request, "文件上传成功！")
                return redirect('task_list')
            except Exception as e:
                return HttpResponse(f"文件上传失败！{e}")
    else:
        form = UploadExcelForm()
    return render(request, 'upload_excel.html',  {'form': form})


def __create_tasks(task_names, status, project, sub_project, iteration, team_member, alias, is_reporting_to_me):
    created_tasks = []
    if not task_names:
        return created_tasks
    for name in task_names:
        task = Task(
            project=project,
            sub_project=sub_project,
            iteration=iteration,  # 固定迭代为 2022Q1
            team_member=team_member,
            alias=alias,
            is_reporting_to_me=is_reporting_to_me,
            name=name.strip(),  # 去掉前后空格
            status=status,
        )
        created_tasks.append(task)
    return created_tasks


def success(request):
    return render(request, 'success.html')


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


def task_edit(request, pk):
    task = Task.objects.get(pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')  # 重定向到任务列表页面

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


def task_report(request):
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday() + 7)
    end_date = today - timedelta(days=today.weekday())
    report = Task.objects.filter(created_at__range=[start_date, end_date]).aggregate(Sum('actual_hours'))
    return render(request, 'tasks/task_report.html', {'report': report})


def home(request):
    return render(request, 'home.html')
