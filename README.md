# 🗂️ Django Task Management System

A Django-based web application and RESTful API to manage users, assign tasks, and track their progress using role-based access and JWT authentication.

## 🚀 Features

- 🔐 **User Registration and Login**
- 👥 **Role-Based Access** (Super Admin, Admin, User)
- 📝 **Task Creation and Assignment** by Admins
- ⬆️⬇️ **Admin Promotion and Demotion** by Super Admins
- 📊 **Task Status Tracking** (Pending, In Progress, Completed)
- 📋 **Dashboard** for task/user management (Admin & Super Admin)
- 🧑‍💼 **Each Admin Has Their Own Users** – fully segregated task control
- ⏱️ **Users Submit Task Completion Report and Worked Hours**
- 🔧 **Admin Panel** for managing everything
- 📱 **Responsive Design** for mobile and desktop
- 🔑 **JWT Token Generation** on user login
- 🌐 **REST API for Users' Activity** (with secured endpoints)

## 🛠 Tech Stack

- **Backend**: Python, Django, Django REST Framework (DRF)
- **Frontend**: HTML, CSS, JavaScript (optional: Bootstrap)
- **Authentication**: JWT via Simple JWT
- **Database**: SQLite 

## 🔁 API Highlights

- JWT-based login and access control
- Endpoints for:
  - User activity logs
  - Task Response operations
  - Submission of completion reports





