from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('', views.admin_dashboard, name='admin_panel_dashboard'),
    path('users/', views.admin_users, name='admin_panel_users'),
    path('users/<int:user_id>/role/', views.admin_user_role_change, name='admin_panel_user_role'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='admin_panel_user_delete'),
    path('courses/', views.admin_courses, name='admin_panel_courses'),
    path('courses/add/', views.admin_course_add, name='admin_panel_course_add'),
    path('courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_panel_course_edit'),
    path('courses/<int:course_id>/delete/', views.admin_course_delete, name='admin_panel_course_delete'),
    path('courses/<int:course_id>/toggle/', views.admin_course_toggle_publish, name='admin_panel_course_toggle'),
    path('enrollments/', views.admin_enrollments, name='admin_panel_enrollments'),
    path('enrollments/<int:enrollment_id>/approve/', views.admin_enrollment_approve, name='admin_panel_enrollment_approve'),
    path('enrollments/<int:enrollment_id>/reject/', views.admin_enrollment_reject, name='admin_panel_enrollment_reject'),
    path('certificates/', views.admin_certificates, name='admin_panel_certificates'),
    path('quizzes/', views.admin_quizzes, name='admin_panel_quizzes'),
]
