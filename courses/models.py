from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    duration = models.CharField(max_length=50, help_text="e.g. 5 Hours, 4 Weeks")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Qiimaha koorsada USD (0 = Bilaash)")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_free(self):
        return self.price == 0

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @property
    def total_reviews(self):
        return self.reviews.count()

    def get_user_progress(self, user):
        """Calculate progress percentage (0-100) for a given user."""
        if not user or not user.is_authenticated:
            return 0
        total = self.lessons.count()
        if total == 0:
            return 0
        completed_count = LessonProgress.objects.filter(
            user=user,
            lesson__course=self,
            completed=True
        ).count()
        return int((completed_count / total) * 100)

    def is_enrolled_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.enrollments.filter(user=user, status='approved').exists()

    def get_enrollment_status(self, user):
        if not user or not user.is_authenticated:
            return None
        enrollment = self.enrollments.filter(user=user).first()
        return enrollment.status if enrollment else None


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True, help_text="Optional link to video lesson")
    order = models.PositiveIntegerField(default=1)
    is_free_preview = models.BooleanField(default=False, help_text="Casharkan ma u furan yahay arday kasta (Free Preview)?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"

    def is_completed_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return LessonProgress.objects.filter(user=user, lesson=self, completed=True).exists()

    @property
    def embed_video_url(self):
        if not self.video_url:
            return None
        import re
        yt_match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', self.video_url)
        if yt_match:
            video_id = yt_match.group(1)
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        if 'embed' in self.video_url:
            return self.video_url
        return None


class LessonResource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lesson_resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text="External resource link")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resource: {self.title} ({self.lesson.title})"


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('approved', 'Fasaxan (Approved)'),
        ('pending', 'Sugitaan (Pending Approval)'),
        ('rejected', 'La Diiday (Rejected)'),
    )

    PAYMENT_METHODS = (
        ('Zaad', 'Telesom Zaad'),
        ('e-Dahab', 'Dahabshiil e-Dahab'),
        ('EVC Plus', 'Hormuud EVC Plus'),
        ('Free', 'Bilaash (Free Enrollment)'),
        ('Manual', 'Gacanta (Manual Admin)'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='Free')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction reference number")
    payment_receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    approved_at = models.DateTimeField(blank=True, null=True)
    admin_notes = models.TextField(blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.get_status_display()})"

    @property
    def is_active(self):
        return self.status == 'approved'


class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        status = "Completed" if self.completed else "In Progress"
        return f"{self.user.username} - {self.lesson.title} ({status})"


import uuid

class Review(models.Model):
    RATING_CHOICES = (
        (5, '★★★★★ (5/5 Excellent)'),
        (4, '★★★★☆ (4/5 Very Good)'),
        (3, '★★★☆☆ (3/5 Good)'),
        (2, '★★☆☆☆ (2/5 Fair)'),
        (1, '★☆☆☆☆ (1/5 Poor)'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}★)"


class Quiz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pass_percentage = models.PositiveIntegerField(default=70, help_text="Passing score percentage (e.g. 70%)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.title} ({self.course.title})"

    @property
    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        marker = "✓" if self.is_correct else "✗"
        return f"[{marker}] {self.text}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(help_text="Achieved score percentage (0-100)")
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"{self.user.username} - {self.quiz.title}: {self.score}% ({status})"


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_code = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate: {self.user.username} - {self.course.title} ({self.certificate_code[:8]})"

