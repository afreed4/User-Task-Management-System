from user_accounts.models import TaskModel,Workers,User
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.validators import MaxLengthValidator
from datetime import datetime
from django.contrib.auth import get_user_model


# class TaskAddForm(forms.ModelForm):
#     class Meta:
#         model=TaskModel
#         fields=['assigned_to','task_name','task_description','task_status','due_date']
#         widgets={
#                 'assigned_to':forms.ChoiceField(attrs={'class': 'form-control class1', 'placeholder': 'Name'}),
#         }