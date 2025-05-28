from django.db import models
import re
from django.contrib.auth.models import Permission, Group
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms import ValidationError
from django.utils import timezone
import random
from django.core.validators import RegexValidator
import phonenumbers
from django.conf import settings
import uuid
from django.db import models
from PIL import Image
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth.models import AbstractUser


phone_regex = RegexValidator(
    regex=r"^\d{9,15}$", message="Phone number must be between 9 and 15 digits."
)


def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    return value


GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]

PROGRESSION_STATUS_CHOICES = [
    ("not_started", "Not Started"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
]


class Country_Codes(models.Model):
    country_name = models.CharField(max_length=100, unique=True)
    calling_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.country_name} ({self.calling_code})"

    class Meta:
        ordering = ["calling_code"]


class State(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


#
#


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    # Role-based fields

    is_user = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # SuperAdmin-related fields
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    # Any other fields common to both roles
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=30)
    district = models.ForeignKey(
        "District", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    joining_date = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, unique=True, validators=[phone_regex], null=True, blank=True
    )
    country_code = models.ForeignKey(
        Country_Codes, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,blank=True,null=True)

    # custom_id=models.CharField(max_length=100,unique=True,editable=False,blank=True,null=True)

    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    # objects = UserManager()

    groups = models.ManyToManyField(
        Group,
        related_name="app1_user_groups",  # Add a unique related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    # Override user_permissions field with a unique related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        related_name="app1_user_permissions",  # Add a unique related_name
    )

    def __str__(self):
        return self.username if self.username else self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        if not self.state:
            self.state = None
        if not self.district:
            self.district = None
        super(User, self).save(*args, **kwargs)


class TaskModel(models.Model):
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    aassigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_by"
    )
    task_name = models.CharField(max_length=255)
    task_description = models.TextField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name


class UserTaskResponse(models.Model):
    task = models.ForeignKey(TaskModel, on_delete=models.CASCADE)
    task_status = models.CharField(
        max_length=50, choices=PROGRESSION_STATUS_CHOICES, default="not_started"
    )
    completion_report = models.TextField(null=True, blank=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)


class Workers(models.Model):
    under = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="managed_by"
    )  # This is the user who is managing this worker
    worker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="workers"
    )  # This is the worker being managed
