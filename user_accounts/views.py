from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from user_accounts.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
from datetime import timedelta
from django.core.paginator import Paginator


class FetchAllTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_list = []
        task_status_changable = "not started"
        user = request.user
        try:
            user_obj = User.objects.get(username=user.username)
            user_task_obj = TaskModel.objects.filter(assigned_to=user_obj).order_by(
                "id"
            )
        except TaskModel.DoesNotExist:
            return Response({"error": "No task found for this user"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if TaskModel.objects.exists():
            user_response_obj = UserTaskResponse.objects.filter(task__in=user_task_obj)
            response_map = {resp.id: resp.task_status for resp in user_response_obj}
        else:
            return Response({"error": "No task found for this user"}, status=404)

        for x in user_task_obj:
            data_list.append(
                {
                    "task_id": x.id,
                    "task_name": x.task_name,
                    "task_description": x.task_description,
                    "due_date": x.due_date,
                    "assigned_date": x.assigned_date,
                    "task_status": response_map.get(x.id, "Not Started"),
                }
            )

        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)

        paginator = Paginator(data_list, page_size)
        page_obj = paginator.get_page(page_number)

        if data_list:
            return Response(
                {
                    "data": list(page_obj),
                    "total_pages": paginator.num_pages,
                    "current_page": page_obj.number,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                    "message": "Task Fetched Successfully",
                },
                status=200,
            )
        else:
            return Response({"error": "No task found for this user"}, status=404)


class UpdateTaskResponse(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = json.loads(request.body)
        task_id = data.get("task_id")
        task_status = data.get("task_status")
        completion_report = data.get("completion_report")
        worked_hours = data.get("worked_hours")

        if not task_id:
            return Response({"error": "Task ID is required"}, status=400)

        if task_status.lower() == "completed":
            if not completion_report or not worked_hours:
                return Response(
                    {
                        "error": "Completion report and worked hours are required when marking task as Completed."
                    },
                    status=400,
                )

        ALLOWED_STATUSES = {"not_started", "in_progress", "completed"}

        if task_status not in ALLOWED_STATUSES:
            return Response({"error": "Invalid task status."}, status=400)

        elif task_status == "in_progress" and completion_report:
            return Response(
                {
                    "error": "Cannot upload completion report when task status is In Progress."
                },
                status=400,
            )

        try:
            user_obj = User.objects.get(username=user.username)
            task_obj = TaskModel.objects.get(id=task_id, assigned_to=user_obj)
        except TaskModel.DoesNotExist:
            return Response(
                {"error": "Task does not exist or the task is not assigned for you."},
                status=404,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        if UserTaskResponse.objects.filter(task=task_obj).exists():
            task_response_obj = UserTaskResponse.objects.filter(task=task_obj).first()
            task_response_obj.task_status = task_status
            task_response_obj.completion_report = completion_report
            task_response_obj.worked_hours = worked_hours
            task_response_obj.save()
            return Response(
                {"message": "Task response updated successfully"}, status=200
            )

        else:
            task_response_obj = UserTaskResponse.objects.create(
                task=task_obj,
                task_status=task_status,
                completion_report=completion_report,
                worked_hours=worked_hours,
            )
            task_response_obj.save()
            return Response(
                {"message": "Task response created successfully"}, status=201
            )
