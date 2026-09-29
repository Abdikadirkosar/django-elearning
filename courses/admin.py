from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Lesson, LessonResource, LessonComment,
    Enrollment, LessonProgress,
    Review, Quiz, Question, Choice, QuizAttempt, Certificate
)


# ─── Inlines ──────────────────────────────────────────────────────────────────
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('order', 'title', 'is_free_preview', 'video_url')
    ordering = ('order',)
    show_change_link = True


class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0
    fields = ('title', 'file', 'url')


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ('text', 'is_correct')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('order', 'text', 'explanation')
    show_change_link = True


# ─── Course ───────────────────────────────────────────────────────────────────
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price_display', 'duration', 'is_published', 'enrollment_count', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor', 'category')
    ordering = ('-created_at',)
    list_editable = ('is_published',)
    inlines = [LessonInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        ('📚 Course Info', {
            'fields': ('title', 'description', 'category', 'instructor', 'image')
        }),
        ('💰 Pricing', {
            'fields': ('price', 'duration')
        }),
        ('⚙️ Settings', {
            'fields': ('is_published', 'created_at')
        }),
    )

    def price_display(self, obj):
        if obj.price and obj.price > 0:
            return format_html('<span style="color:#22c55e;font-weight:700;">${}</span>', obj.price)
        return format_html('<span style="color:#818cf8;">FREE</span>')
    price_display.short_description = 'Price'

    def enrollment_count(self, obj):
        count = obj.enrollments.count()
        return format_html('<strong>{}</strong>', count)
    enrollment_count.short_description = '👥 Enrollments'


# ─── Lesson ───────────────────────────────────────────────────────────────────
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_free_preview', 'created_at')
    list_filter = ('course', 'is_free_preview', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    ordering = ('course', 'order')
    list_editable = ('is_free_preview',)
    inlines = [LessonResourceInline]


# ─── LessonResource ───────────────────────────────────────────────────────────
@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'file', 'url', 'created_at')
    list_filter = ('created_at', 'lesson__course')
    search_fields = ('title', 'lesson__title')
    ordering = ('-created_at',)


# ─── LessonComment ────────────────────────────────────────────────────────────
@admin.register(LessonComment)
class LessonCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'short_comment', 'created_at')
    list_filter = ('created_at', 'lesson__course')
    search_fields = ('user__username', 'lesson__title', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def short_comment(self, obj):
        return obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = 'Comment'


# ─── Enrollment ───────────────────────────────────────────────────────────────
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status_badge', 'payment_method', 'amount_paid', 'enrolled_at', 'approved_at')
    list_filter = ('status', 'payment_method', 'enrolled_at', 'course')
    search_fields = ('user__username', 'course__title', 'transaction_id')
    ordering = ('-enrolled_at',)
    readonly_fields = ('enrolled_at', 'approved_at')
    fieldsets = (
        ('👤 Ardayga', {
            'fields': ('user', 'course')
        }),
        ('💳 Lacag Bixinta', {
            'fields': ('payment_method', 'transaction_id', 'payment_receipt', 'amount_paid')
        }),
        ('✅ Ansixinta', {
            'fields': ('status', 'admin_notes', 'approved_at', 'enrolled_at')
        }),
    )
    actions = ['approve_enrollments', 'reject_enrollments']

    def status_badge(self, obj):
        colors = {
            'pending':  ('#f59e0b', '#fffbeb'),
            'approved': ('#22c55e', '#f0fdf4'),
            'rejected': ('#ef4444', '#fef2f2'),
        }
        color, bg = colors.get(obj.status, ('#64748b', '#f8fafc'))
        return format_html(
            '<span style="color:{};background:{};padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:700;">{}</span>',
            color, bg, obj.status.title()
        )
    status_badge.short_description = 'Status'

    def approve_enrollments(self, request, queryset):
        from django.utils import timezone
        from accounts.models import Notification
        from django.urls import reverse
        updated = 0
        for enrollment in queryset.filter(status='pending'):
            enrollment.status = 'approved'
            enrollment.approved_at = timezone.now()
            enrollment.save()
            Notification.objects.create(
                user=enrollment.user,
                title="🎉 Koorsadaadii Waa La Fasaxay!",
                message=f"Dalabkaagii koorsada '{enrollment.course.title}' waa la ansixiyay.",
                link=reverse('course_detail', kwargs={'pk': enrollment.course.id})
            )
            updated += 1
        self.message_user(request, f"✅ {updated} dalabood waa la ansixiyay.")
    approve_enrollments.short_description = "✅ Ansiri Dalabada Xulashada"

    def reject_enrollments(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"❌ {updated} dalabood waa la diiday.")
    reject_enrollments.short_description = "❌ Diid Dalabada Xulashada"


# ─── LessonProgress ───────────────────────────────────────────────────────────
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')
    ordering = ('-completed_at',)


# ─── Review ───────────────────────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'stars_display', 'short_comment', 'created_at')
    list_filter = ('rating', 'created_at', 'course')
    search_fields = ('user__username', 'course__title', 'comment')
    ordering = ('-created_at',)

    def stars_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span title="{}/5">{}</span>', obj.rating, stars)
    stars_display.short_description = 'Rating'

    def short_comment(self, obj):
        return (obj.comment or '')[:60]
    short_comment.short_description = 'Comment'


# ─── Quiz ─────────────────────────────────────────────────────────────────────
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_percentage', 'question_count', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    inlines = [QuestionInline]

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = '❓ Questions'


# ─── Question ─────────────────────────────────────────────────────────────────
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'order', 'short_text')
    list_filter = ('quiz__course',)
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]
    ordering = ('quiz', 'order')

    def short_text(self, obj):
        return obj.text[:70] + '...' if len(obj.text) > 70 else obj.text
    short_text.short_description = 'Question'


# ─── QuizAttempt ──────────────────────────────────────────────────────────────
@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score_display', 'passed_badge', 'completed_at')
    list_filter = ('passed', 'completed_at', 'quiz__course')
    search_fields = ('user__username', 'quiz__title')
    ordering = ('-completed_at',)
    readonly_fields = ('completed_at',)

    def score_display(self, obj):
        color = '#22c55e' if obj.passed else '#ef4444'
        return format_html('<strong style="color:{};">{:.1f}%</strong>', color, obj.score)
    score_display.short_description = 'Score'

    def passed_badge(self, obj):
        if obj.passed:
            return format_html('<span style="color:#22c55e;font-weight:700;">✅ Passed</span>')
        return format_html('<span style="color:#ef4444;font-weight:700;">❌ Failed</span>')
    passed_badge.short_description = 'Result'


# ─── Certificate ──────────────────────────────────────────────────────────────
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_code', 'user', 'course', 'issued_at')
    search_fields = ('certificate_code', 'user__username', 'course__title')
    list_filter = ('issued_at', 'course')
    ordering = ('-issued_at',)
    readonly_fields = ('certificate_code', 'issued_at')
