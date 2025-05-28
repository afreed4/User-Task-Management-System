from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user_accounts.models import *
from . import urls
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse


# Create your views here.
def super_admin_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            # Authenticate the user
            print(username, password)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    messages.success(request, "Login successful!")
                    login(request, user)
                    return redirect("staff_view")
                else:
                    messages.error(
                        request, "You are not authorized to access this page."
                    )
                    return render(
                        request,
                        "super_admin_dash/super_admin_login.html",
                        {"error": "You are not authorized to access this page."},
                    )
            else:
                messages.error(request, "Invalid username or password")
                return render(
                    request,
                    "super_admin_dash/super_admin_login.html",
                    {"error": "Invalid username or password"},
                )

    return render(request, "super_admin_dash/super_admin_login.html")


@login_required(login_url="super_admin_login")
def list_staff(request):
    if request.user.is_authenticated:
        try:
            super_admin_user = request.user
            super_user_obj = User.objects.get(username=super_admin_user.username)
        except User.DoesNotExist:
            messages.error(request, "Super admin user not found.")
            return render(
                request,
                "super_admin_templates/super_manage_staff.html",
                {"error": "Super admin user not found."},
            )

        if super_user_obj.is_superuser:
            users_list = User.objects.all().exclude(username=super_admin_user.username)
            return render(
                request,
                "super_admin_templates/super_manage_staff.html",
                {"users_list": users_list},
            )
        else:
            messages.error(request, "You are not authorized to access this page.")
            return render(
                request,
                "super_admin_dash/super_admin_login.html",
                {"error": "You are not authorized to access this page."},
            )


@login_required(login_url="super_admin_login")
def manage_admin(request):
    if request.user.is_authenticated:
        try:
            super_admin_user = request.user
            super_user_obj = User.objects.get(username=super_admin_user.username)
        except User.DoesNotExist:
            messages.error(request, "Super admin user not found.")
            return render(
                request,
                "super_admin_templates/manage_admin.html",
                {"error": "Super admin user not found."},
            )

        if super_user_obj.is_superuser:
            users_list = User.objects.filter(is_admin=True)
            return render(
                request,
                "super_admin_templates/manage_admin.html",
                {"users_list": users_list},
            )
        else:
            messages.error(request, "You are not authorized to access this page.")
            return render(
                request,
                "super_admin_templates/manage_admin.html",
                {"error": "You are not authorized to access this page."},
            )


@login_required(login_url="super_admin_login")
def promote_to_admin(request, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
        if user_obj.is_admin:
            messages.error(request, "User is already an admin.")
            return redirect("edit_staff", user_id=user_id)
        user_obj.is_user = False
        user_obj.is_admin = True
        user_obj.save()
        messages.success(request, "User promoted to admin successfully.")
        return redirect("edit_staff", user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect("edit_staff", user_id=user_id)


@login_required(login_url="super_admin_login")
def demote_from_admin(request, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
        if user_obj.is_admin:
            user_obj.is_admin = False
            user_obj.is_user = True
            user_obj.save()
            messages.success(request, "User demoted from admin successfully.")
            return redirect("edit_staff", user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect("edit_staff", user_id=user_id)


@login_required(login_url="super_admin_login")
def edit_staff(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    default_admin_obj = Workers.objects.filter(worker=user_obj).first()

    if user_obj.is_user and not default_admin_obj:
        messages.error(request, "Admin assignment for this user does not exist.")

    states = State.objects.all()
    admin_list = User.objects.filter(is_admin=True)
    if request.method == "POST":
        try:
            user_obj.full_name = request.POST.get("full_name")
            user_obj.address = request.POST.get("address")
            user_obj.email = request.POST.get("email")
            user_obj.phone_number = request.POST.get("phone_number")
            user_obj.username = request.POST.get("username")
            state = request.POST.get("state")
            district = request.POST.get("district")
            change_admin_var = request.POST.get("change-admin")

            print(state, district, change_admin_var)

            
            district_obj = District.objects.get(name=district)
            state_obj = State.objects.get(name=state)
            new_admin_obj = User.objects.get(id=change_admin_var)
            

            print(district_obj, state_obj)

            user_obj.state = state_obj
            user_obj.district = district_obj
            user_obj.save()
            
            Workers.objects.filter(worker=user_obj).delete()
            Workers.objects.create(under=new_admin_obj, worker=user_obj)
           

            if user_obj.is_admin:
                return redirect("manage_admin")
            elif user_obj.is_user:
                return redirect("manage_users")
        except User.DoesNotExist:

            messages.error(request, "User not found.")
            if user_obj.is_admin:
                return redirect("manage_admin")
            elif user_obj.is_user:
                return redirect("manage_users")
    return render(
        request,
        "super_admin_templates/edit_staff.html",
        {
            "user_obj": user_obj,
            "states": states,
            "admin_list": admin_list,
            "default_admin": default_admin_obj,
        },
    )


@login_required(login_url="super_admin_login")
def view_staff(request, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
        print(user_obj.address)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("staff_view")
    return render(
        request, "super_admin_templates/view_staff.html", {"user_obj": user_obj}
    )


def get_districts(request):
    state_id = request.GET.get("state_id")
    districts = District.objects.filter(state__id=state_id).values("id", "name")
    return JsonResponse(list(districts), safe=False)


@login_required(login_url="super_admin_login")
def create_admin(request):
    states = State.objects.all()
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        state = request.POST.get("state")
        district = request.POST.get("district")
        gender = request.POST.get("gender")
      

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("create_admin")

        district_obj = District.objects.get(id=district)
        state_obj = State.objects.get(id=state)
        try:
            user_obj = User.objects.create_user(
                username=username,
                password=password,
                gender=gender,
                full_name=(
                    full_name
                    if full_name
                    else messages.error(request, "Full name is required.")
                ),
                email=email if email else messages.error(request, "Email is required."),
                phone_number=(
                    phone_number
                    if phone_number
                    else messages.error(request, "Phone number is required.")
                ),
                address=address,
                is_admin=True,  # Set is_admin to True for admin users
                state=state_obj,
                district=district_obj,
            )

            messages.success(request, "User created successfully!")
            return redirect("manage_admin")
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("create_admin")

    return render(
        request, "super_admin_templates/create_admin.html", {"states": states}
    )


@login_required(login_url="super_admin_login")
def delete_user(request, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
        user_obj.delete()
        messages.success(request, "User deleted successfully!")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")

    return redirect("staff_view")


@login_required(login_url="super_admin_login")
def manage_users(request):
    data_list = []
    users_obj = User.objects.filter(is_user=True)
    if Workers.objects.filter(worker__in=users_obj):
        managed_by = Workers.objects.filter(worker__in=users_obj)
        if not managed_by:
            messages.error(request, "Admin assignment for this user does not exist.")
            return redirect("edit_staff")
        user_to_manager = {w.worker.id: w.under.username for w in managed_by}
        for x in users_obj:
            data_list.append(
                {
                    "id": x.id,
                    "full_name": x.full_name,
                    "username": x.username,
                    "email": x.email,
                    "phone_number": x.phone_number,
                    "district": x.district,
                    "state": x.state,
                    "managed_by": user_to_manager.get(
                        x.id, "N/A"
                    ),  # fallback if no manager
                }
            )

    return render(
        request, "super_admin_templates/manage_users.html", {"data_list": data_list}
    )


login_required(login_url="super_admin_login")


def create_user(request):
    states = State.objects.all()
    admin_list = User.objects.filter(is_admin=True)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        state = request.POST.get("state")
        district = request.POST.get("district")

        admin_name = request.POST.get("admin-select")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("create_user")

        district_obj = District.objects.get(id=district)
        state_obj = State.objects.get(id=state)

        try:
            admin_obj = User.objects.get(username=admin_name)

            print(admin_obj, "admin obj")
        except User.DoesNotExist:
            messages.error(request, "Could not find the selected Admin")
            return redirect("create_user")
        try:
            user_obj = User.objects.create_user(
                username=username,
                password=password,
                full_name=(
                    full_name
                    if full_name
                    else messages.error(request, "Full name is required.")
                ),
                email=email if email else messages.error(request, "Email is required."),
                phone_number=(
                    phone_number
                    if phone_number
                    else messages.error(request, "Phone number is required.")
                ),
                address=address,
                is_user=True,
                state=state_obj,
                district=district_obj,
            )

            worker_obj = Workers.objects.create(under=admin_obj, worker=user_obj)

            messages.success(request, "User created successfully!")
            return redirect("manage_users")
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("create_user")
    return render(
        request,
        "super_admin_templates/create_user.html",
        {"states": states, "admin_list": admin_list},
    )


@login_required(login_url="super_admin_login")
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("super_admin_login")


@login_required(login_url="super_admin_login")
def fetch_all_task(request):
    data_list = []
    try:
        task_obj = TaskModel.objects.all()
        for x in task_obj:
            if UserTaskResponse.objects.filter(task=x).exists():
                task_response_obj = UserTaskResponse.objects.filter(task=x).first()
                data_list.append(
                    {
                        "task_id": x.id,
                        "task_name": x.task_name,
                        "task_description": x.task_description,
                        "assigned_to": x.assigned_to.username,
                        "assigned_by": x.aassigned_by.username,
                        "due_date": x.due_date,
                        "task_status": (
                            task_response_obj.task_status
                            if task_response_obj
                            else "Not Started"
                        ),
                        "completion_report": (
                            task_response_obj.completion_report
                            if task_response_obj.task_status == "completed"
                            or "Completed"
                            else "No Report available"
                        ),
                        "worked_hours": (
                            task_response_obj.worked_hours
                            if task_response_obj
                            else "0.00"
                        ),
                        "assigned_date": x.assigned_date.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            else:
                data_list.append(
                    {
                        "task_id": x.id,
                        "task_name": x.task_name,
                        "task_description": x.task_description,
                        "assigned_to": x.assigned_to.username,
                        "assigned_by": x.aassigned_by.username,
                        "due_date": x.due_date,
                        "task_status": "Not Started",
                        "completion_report": "No Report available",
                        "worked_hours": "0.00",
                        "assigned_date": x.assigned_date.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
    except TaskModel.DoesNotExist:
        messages.error(request, "No tasks found.")
        return render(
            request,
            "super_admin_templates/manage_tasks.html",
            {"error": "No tasks found."},
        )
    return render(
        request, "super_admin_templates/manage_tasks.html", {"data_list": data_list}
    )


login_required(login_url="super_admin_login")


def view_task_details(request, task_id):
    data_list = []
    try:
        task_obj = TaskModel.objects.get(id=task_id)
        if UserTaskResponse.objects.filter(task=task_obj).exists():
            task_response_obj = UserTaskResponse.objects.filter(task=task_obj).first()
            data_list.append(
                {
                    "task_id": task_obj.id,
                    "task_name": task_obj.task_name,
                    "task_description": task_obj.task_description,
                    "assigned_to": task_obj.assigned_to.username,
                    "assigned_by": task_obj.aassigned_by.username,
                    "due_date": task_obj.due_date,
                    "task_status": (
                        task_response_obj.task_status
                        if task_response_obj
                        else "Not Started"
                    ),
                    "completion_report": (
                        task_response_obj.completion_report
                        if task_response_obj
                        and (
                            task_response_obj.task_status == "completed"
                            or task_response_obj.task_status == "Completed"
                        )
                        else "No Report available"
                    ),
                    "worked_hours": (
                        task_response_obj.worked_hours if task_response_obj else "0.00"
                    ),
                    "assigned_date": task_obj.assigned_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
        else:
            data_list.append(
                {
                    "task_id": task_obj.id,
                    "task_name": task_obj.task_name,
                    "task_description": task_obj.task_description,
                    "assigned_to": task_obj.assigned_to.username,
                    "assigned_by": task_obj.aassigned_by.username,
                    "due_date": task_obj.due_date,
                    "task_status": "Not Started",
                    "completion_report": "No Report available",
                    "worked_hours": "0.00",
                    "assigned_date": task_obj.assigned_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")
        return redirect("manage_tasks")
    return render(
        request, "super_admin_templates/view_task.html", {"data_list": data_list}
    )


def get_users_of_each_admin(request):
    admin_id = request.GET.get("admin_id")
    workers = Workers.objects.filter(under__id=admin_id).values(
        "worker__id", "worker__username"
    )
    print(workers)
    return JsonResponse(list(workers), safe=False)


login_required(login_url="super_admin_login")
def edit_task(request, task_id):
    all_admins = User.objects.filter(is_admin=True).values("id", "username")
    try:
        task_obj = TaskModel.objects.get(id=task_id)
    except TaskModel.DoesNotExist:
        messages.error(request, "Task does not exist.")
        return redirect("manage_tasks")

    if request.method == "POST":
        try:
            task_obj.task_name = request.POST.get("task_name")
            task_obj.task_description = request.POST.get("task_description")
            task_obj.due_date = request.POST.get("due_date")
            assigned_by = request.POST.get("admin-select")
            if assigned_by:
                try:
                    assigned_by_obj = User.objects.get(username=assigned_to)
                    task_obj.assigned_by = assigned_by_obj
                except User.DoesNotExist:
                    messages.error(request, "Assigned admin does not exist.")
                    return redirect("edit_task", task_id=task_id)
            assigned_to = request.POST.get("users-select")
            if assigned_to:
                try:
                    assigned_to_obj = User.objects.get(username=assigned_to)
                    task_obj.assigned_to = assigned_to_obj
                except User.DoesNotExist:
                    messages.error(request, "Assigned user does not exist.")
                    return redirect("edit_task", task_id=task_id)
            task_obj.save()
        except Exception as e:
            messages.error(request, f"Error updating task: {str(e)}")
            return redirect("edit_task", task_id=task_id)
    return render(
        request,
        "super_admin_templates/edit_task.html",
        {"all_admins": all_admins, "task_obj": task_obj},
    )


login_required(login_url="super_admin_login")
def create_task(request):
    all_admins = User.objects.filter(is_admin=True).values("id", "username")
    if request.method == "POST":
        task_name = request.POST.get("task_name")
        task_description = request.POST.get("task_description")
        due_date = request.POST.get("due_date")
        assigned_to = request.POST.get("users-select")
        assigned_by = request.POST.get("admin-select")

        print(assigned_by, assigned_to)

        if not task_name or not assigned_to or not assigned_by:
            messages.error(
                request, "Task name , assigned user and assigned by user are required."
            )
            return redirect("super_create_task")

        try:
            assigned_to_obj = User.objects.get(id=assigned_to)
            assigned_by_obj = User.objects.get(id=assigned_by)
            print("this is user obj", assigned_to_obj, assigned_by_obj)

            task_obj = TaskModel.objects.create(
                task_name=task_name,
                task_description=task_description,
                due_date=due_date,
                assigned_to=assigned_to_obj,
                aassigned_by=assigned_by_obj,
            )
            messages.success(request, "Task created successfully!")
            return redirect("manage_tasks")
        except User.DoesNotExist:
            messages.error(request, "Assigned user does not exist.")
            return redirect("super_create_task")

    return render(
        request, "super_admin_templates/create_task.html", {"all_admins": all_admins}
    )


login_required(login_url="super_admin_login")
def delete_task(request, task_id):
    try:
        task_obj = TaskModel.objects.get(id=task_id)
        task_obj.delete()
        messages.success(request, "Task deleted successfully ")
    except TaskModel.DoesNotExist:
        messages.error(request, "Could not locate the task")
        return redirect("manage_tasks")


login_required(login_url="super_admin_login")
def fetch_completed_task(request):
    completed_task_obj = UserTaskResponse.objects.filter(
        task_status__in=["completed", "Completed"]
    )
    print(completed_task_obj)
    return render(
        request,
        "super_admin_templates/completed_task.html",
        {"completed_task_obj": completed_task_obj},
    )
