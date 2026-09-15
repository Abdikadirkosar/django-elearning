from django.contrib import admin
from .models import Course, Lesson, Enrollment, LessonProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'video_url')
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'duration', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor', 'category')
    ordering = ('-created_at',)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    ordering = ('-enrolled_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at')
    search_fields = ('user__username', 'lesson__title')


from .models import Review, Quiz, Question, Choice, QuizAttempt, Certificate


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'course')
    search_fields = ('user__username', 'course__title', 'comment')


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'order', 'text')
    list_filter = ('quiz__course',)
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('order', 'text', 'explanation')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_percentage', 'created_at')
    search_fields = ('title', 'course__title')
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'completed_at')
    list_filter = ('passed', 'completed_at')
    search_fields = ('user__username', 'quiz__title')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_code', 'user', 'course', 'issued_at')
    search_fields = ('certificate_code', 'user__username', 'course__title')
    list_filter = ('issued_at', 'course')

