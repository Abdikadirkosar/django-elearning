from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:pk>/checkout/', views.course_checkout, name='course_checkout'),
    path('courses/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('courses/<int:pk>/quiz/', views.take_quiz, name='take_quiz'),
    path('courses/<int:pk>/certificate/', views.view_certificate, name='view_certificate'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:pk>/comment/', views.add_lesson_comment, name='add_lesson_comment'),
    path('lessons/<int:pk>/complete/', views.complete_lesson, name='complete_lesson'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('certificate/verify/<str:code>/', views.verify_certificate_view, name='verify_certificate'),
]
