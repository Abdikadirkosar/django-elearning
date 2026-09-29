from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Customize Django Admin Branding ──────────────────────────────────────────
admin.site.site_header  = "🛡️ AQOONPLUS — Xafiiska Maamulka"
admin.site.site_title   = "AQOONPLUS Admin"
admin.site.index_title  = "⚙️ Maareeyaha Nidaamka | E-Learning Platform"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'courses.views.custom_404_view'
handler500 = 'courses.views.custom_500_view'
handler403 = 'courses.views.custom_403_view'
