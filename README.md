# E-Learn - Simple E-Learning Management System

**Lead Developer**: **Dev. Abdikadir**

"E-Learn" is a full-stack E-Learning Management System (LMS) built with **Python**, **Django 5**, **HTML5**, **CSS3**, **Vanilla JavaScript**, and **SQLite**.

It is architected by **Dev. Abdikadir** to be clean, modular, professional, and easy for a Computer Science student to demonstrate during an academic project presentation.

---

## 🌟 Features

### For Students
- **Interactive Landing Page**: Modern hero section, real-time platform statistics, featured courses, and call-to-action blocks.
- **User Authentication**: Secure user registration, validation, password confirmation, session login, and logout.
- **Course Catalog**: Filter courses by category and perform instant live search using pure Vanilla JavaScript.
- **Course Syllabus & Enrollment**: View course details, syllabus outline, instructor info, and enroll with a single click.
- **Interactive Lesson Player**: Sequential lesson navigation (Previous / Next lesson buttons), video tutorial links, and lesson completion markers.
- **Personalized Student Dashboard**: Real-time stats (Enrolled Courses, Completed Lessons, Overall Progress %, Certificates) and "Continue Learning" shortcuts.

### For Administrators
- **Django Admin Interface**: Full control to manage users, courses, lessons, enrollments, and lesson completion records.
- **Tabular Inline Lessons**: Add or reorder lessons directly inside the Course edit page in Django Admin.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Django 5.x (Auth, Forms, ORM, Admin)
- **Frontend**: HTML5, Vanilla CSS3 (Custom CSS Variables, Grid, Flexbox), Vanilla JavaScript (ES6+)
- **Database**: SQLite3
- **Architecture**: Django MVT (Model-View-Template)

> **Note**: No heavy frontend frameworks (React, Vue, Angular, Bootstrap, Tailwind, or jQuery) were used. The frontend is built from scratch using pure web standards.

---

## 📁 Project Directory Structure

```
django/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
│
├── e_learning/               # Project Root Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── courses/                  # Courses & Lessons App
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py  # Sample Data Generator Command
│   ├── migrations/
│   ├── templates/
│   │   └── courses/
│   │       ├── home.html
│   │       ├── course_list.html
│   │       ├── course_detail.html
│   │       └── lesson_detail.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # Course, Lesson, Enrollment, LessonProgress
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── accounts/                 # User Authentication App
│   ├── templates/
│   │   └── accounts/
│   │       ├── login.html
│   │       └── register.html
│   ├── forms.py              # UserRegisterForm & UserLoginForm
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── dashboard/                # Student Dashboard App
│   ├── templates/
│   │   └── dashboard/
│   │       └── dashboard.html
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── templates/                # Shared Master Templates
│   ├── base.html             # Main Navbar, Footer & Layout
│   ├── 404.html              # Custom 404 Error Page
│   └── 500.html              # Custom 500 Error Page
│
└── static/                   # Static Frontend Assets
    ├── css/
    │   └── style.css         # Modern Vanilla CSS Design System
    └── js/
        └── main.js           # Mobile drawer, search filter, auto-alerts
```

---

## 🚀 Step-by-Step Installation & Setup

### 1. Open Terminal in Project Directory
Navigated to your project root folder:
```bash
cd path/to/django
```

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell / Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
Create the SQLite database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Sample Seed Data
Seed 5 complete courses with 25 interactive lessons into your database:
```bash
python manage.py seed_data
```

### 6. Create Superuser (Admin Account)
Run the administrative user creation wizard:
```bash
python manage.py createsuperuser
```
*(Enter a username, email, and password when prompted)*

### 7. Run the Development Server
```bash
python manage.py runserver 8000
```

Open your browser and visit:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

Django Admin interface is available at:
👉 **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

---

## 🧪 Running Automated Tests

Run Django's built-in test suite to verify project health:
```bash
python manage.py test
```

All test cases covering registration, login, course catalog, enrollments, lesson progress, and dashboard permissions will run and display `OK`.

---

## 🎓 Django MVT Architecture Explained

When presenting to your professor, explain the software flow using Django's **MVT (Model-View-Template)** pattern:

```
[ User Browser ]
       │
       ▼
 [ 1. URL Pattern (urls.py) ]  ─── Maps request path to a View function
       │
       ▼
 [ 2. View Function (views.py) ] ── Executes business logic & security checks
       │                      │
       ▼                      ▼
[ 3. Model (models.py) ]   [ 4. Django ORM ] ── SQL query ──► [ SQLite DB ]
       │                      │                                     │
       └───────────┬──────────┘ ◄── Data Returned ──────────────────┘
                   │
                   ▼
 [ 5. Template (HTML + DTL) ] ── Renders context data into dynamic HTML page
       │
       ▼
[ Rendered HTTP Response to Browser ]
```

1. **Model (`models.py`)**: Defines python data structures (`Course`, `Lesson`, `Enrollment`, `LessonProgress`) mapped to SQLite tables via Django ORM.
2. **View (`views.py`)**: Handles request logic, `@login_required` permissions, form processing, and database querying.
3. **Template (`templates/`)**: Converts Python dictionary data into HTML markup using Django Template Language (`{{ variable }}`, `{% for %}`, `{% if %}`).

---

## 👨‍🏫 Classroom Presentation & Defense Guide

If asked by your teacher during your demonstration:

- **Q: Why did you split the project into `courses`, `accounts`, and `dashboard` apps?**  
  *Answer*: Django promotes modularity. `accounts` manages user identity, `courses` manages core academic content, and `dashboard` aggregates student progress. This makes the codebase clean and maintainable.

- **Q: How is lesson progress calculated?**  
  *Answer*: `Course.get_user_progress(user)` queries `LessonProgress` records for that user and course, divides completed lessons by total lessons, and multiplies by 100 to return an integer percentage.

- **Q: How do you prevent duplicate enrollments?**  
  *Answer*: In `models.py`, `Enrollment` enforces `unique_together = ('user', 'course')`. In `views.py`, we use `Enrollment.objects.get_or_create(...)` to guarantee duplicate protection.

- **Q: How does security work in this project?**  
  *Answer*: All POST forms require `{% csrf_token %}` to prevent Cross-Site Request Forgery. Passwords are hashed using Django's default PBKDF2 algorithm. Sensitive views use `@login_required`.

---

## 🔮 Future Improvements
- PDF Certificate Generation upon 100% course completion.
- Quiz / Assignment submission at the end of each lesson.
- Video file upload support for instructors.
