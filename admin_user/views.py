from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user_accounts.models import *
from . import urls
from django.contrib.auth.decorators import login_required
import json


def admin_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            # Authenticate the user
            print(username, password)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_admin:
                    messages.success(request, "Login successful!")
                    login(request, user)
                    return redirect("admin_dashboard")
                else:
                    messages.error(
                        request, "You are not authorized to access this page."
                    )
                    return render(
                        request,
                        "admin_dash/admin-login.html",
                        {"error": "You are not authorized to access this page."},
                    )
            else:
                messages.error(request, "Invalid username or password")
                return render(
                    request,
                    "admin_dash/admin-login.html",
                    {"error": "Invalid username or password"},
                )

    return render(request, "admin_dash/admin-login.html")


@login_required(login_url="admin_login")
def view_users(request):
    if request.user.is_authenticated:
        admin_user = request.user
        admin_worker_obj = Workers.objects.filter(under=admin_user)

        if not admin_worker_obj.exists():
            return render(
                request,
                "manage_staff_template.html",
                {"error": "No workers found for this admin."},
            )
        for x in admin_worker_obj:
            print(x.worker.username)
        return render(
            request, "manage_staff_template.html", {"worker": admin_worker_obj}
        )
    else:
        return render(request, "admin_dash/admin-login.html")


def fill_user_name(request):
    users_list = []
    admin_user = request.user
    worker_obj = Workers.objects.filter(under=admin_user)

    if not worker_obj.exists():
        return render(request, "create_task.html", {"user_list": users_list})
    else:
        users_list = [x.worker.username for x in worker_obj]
        print(users_list)
    return render(request, "create_task.html", {"user_list": users_list})


@login_required(login_url="admin_login")
def create_task(request):
    fill_user_name(request)
    if request.method == "POST":
        task_name = request.POST.get("task_name")
        task_discription = request.POST.get("task_discription")
        task_assigned_to = request.POST.get("user_name")
        due_date = request.POST.get("due_date")

        if task_assigned_to:
            print(type(task_assigned_to), "task_assigned_to")
        else:
            print("task_assigned_to is empty")
        try:
            assigned_to_obj = User.objects.get(username=task_assigned_to)
            assigned_by_obj = User.objects.get(username=request.user.username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("fill_user_name")

        task_obj = TaskModel.objects.create(
            assigned_to=assigned_to_obj,
            aassigned_by=assigned_by_obj,
            due_date=due_date,
            task_name=task_name,
            task_description=task_discription,
        )
        task_obj.save()
        messages.success(request, "Task created successfully!")

    return render(request, "create_task.html")


@login_required(login_url="admin_login")
def view_task(request):
    user = request.user
    task_status = []
    try:
        user_obj = User.objects.get(username=user.username)
        user_obj_value = TaskModel.objects.filter(aassigned_by=user_obj)
        user_response = UserTaskResponse.objects.filter(task__in=user_obj_value)
        if user_response.exists():
            print("user_response exists")
        else:
            print("user_response does not exist")

    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect("view_task")

    return render(
        request, "view_task.html", {"user": user_obj_value, "task_status": task_status}
    )


@login_required(login_url="admin_login")
def task_details(request, task_id):
    data_set = []
    try:
        task_obj = TaskModel.objects.get(id=task_id)
        task_response = UserTaskResponse.objects.filter(task=task_obj).first()

    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")
        return redirect("view_task")

    return render(
        request, "task_details.html", {"task": task_obj, "task_response": task_response}
    )


def fill_user_list_withdata(request, task_id):
    users_list = []
    admin_user = request.user
    try:
        worker_obj = Workers.objects.filter(under=admin_user)
        task_obj = TaskModel.objects.get(id=task_id)
        print(task_obj.assigned_to.username)
        task_response = UserTaskResponse.objects.filter(task=task_obj).first()
    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")
        return redirect("view_task")

    if not worker_obj.exists():
        return render(request, "edit_task.html", {"user_list": users_list})
    else:
        users_list = [x.worker.username for x in worker_obj]
        print(users_list)

    if task_response and task_response.task_status == "completed":
        messages.error(request, "Task cannot be edited as it is already completed.")
        return redirect("fill_user_list_withdata")

    return render(
        request,
        "edit_task.html",
        {
            "task": task_obj,
            "user_list": users_list,
        },
    )


@login_required(login_url="admin_login")
def edit_task(request, task_id):
    users_list = []
    admin_user = request.user
    try:
        worker_obj = Workers.objects.filter(under=admin_user)
        task_obj = TaskModel.objects.get(id=task_id)
        task_response = UserTaskResponse.objects.filter(task=task_obj).first()
    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")
        return redirect("view_task")

    if not task_response or task_response.task_status != "completed":
        if request.method == "POST":
            task_name = request.POST.get("task_name")
            task_description = request.POST.get("task_description")
            due_date = request.POST.get("due_date")
            assigned_to = request.POST.get("assigned_to")

            if assigned_to:
                try:
                    assigned_to_obj = User.objects.get(username=assigned_to)
                    task_obj.assigned_to = assigned_to_obj
                except User.DoesNotExist:
                    messages.error(request, "Somthing went wrong with the Add user.")
                    return redirect("fill_user_list_withdata", task_id=task_id)
            if task_name:
                task_obj.task_name = task_name
            if task_description:
                task_obj.task_description = task_description
            if due_date:
                task_obj.due_date = due_date
            task_obj.save()

            messages.success(request, "Task Edited successfully!")
            return redirect("fill_user_list_withdata", task_id=task_id)
    else:
        messages.error(request, "Task cannot be edited as it is already completed.")
        return redirect("fill_user_list_withdata", task_id=task_id)

    return render(request, "edit_task.html", {"task": task_obj})


@login_required(login_url="admin_login")
def delete_task(request, task_id):
    try:
        task_obj = TaskModel.objects.get(id=task_id)
        task_obj.delete()
        messages.success(request, "Task deleted successfully!")
    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")

    return redirect("view_task")


@login_required(login_url="admin_login")
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("admin_login")

@login_required(login_url="admin_login")
def admin_fetch_completed_task(request):
    user_obj = User.objects.get(username=request.user.username)
    user_obj_value = TaskModel.objects.filter(aassigned_by=user_obj)
    completed_task_obj = UserTaskResponse.objects.filter(task__in=user_obj_value,task_status__in=["completed", "Completed"])
    
    return render(
        request,
        "completed_task.html",
        {"completed_task_obj": completed_task_obj},
    )
