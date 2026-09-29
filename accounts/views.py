from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
    ChangePasswordForm,
)
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Akoon cusub ayaa loo sameeyay {user.username}! Hadda waad gali kartaa.")
                return redirect('login')
            except IntegrityError:
                form.add_error('username', "Magacan isticmaale hore ayaa loo qaatay. Fadlan dooro mid kale.")
                messages.error(request, "Diiwaangelintu way fashilantay. Magaca ama email-ka ayaa horay u jiray.")
        else:
            messages.error(request, "Fadlan sax khaladaadka hoose ku qoran.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('username').strip()
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', True)

            # Support Login with Email OR Username
            user = None
            if '@' in identifier:
                user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = authenticate(request, username=identifier, password=password)

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks remember me

                messages.success(request, f"Ku soo dhawoow mar kale, {user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                # Redirect based on role
                try:
                    if user.is_superuser or user.profile.role == 'admin':
                        return redirect('admin_panel_dashboard')
                except Exception:
                    pass
                return redirect('dashboard')
            else:
                messages.error(request, "Magaca isticmaalaha (ama email-ka) ama furaha sirta ah ma saxna.")
        else:
            messages.error(request, "Fadlan buuxi dhammaan meelaha loo baahan yahay.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Si guul leh ayaad uga baxday akoonkaaga.")
    return redirect('home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Xogtaada profile-ka si guul leh ayaa loo cusbooneysiiyay!")
            return redirect('profile')
        else:
            messages.error(request, "Fadlan sax khaladaadka hoos ku xusan.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


# ===================== PASSWORD RESET VIEWS =====================

def password_reset_request_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier').strip()
            user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
            
            reset_url = None
            if user and user.email:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
                )
                
                # Send email via console/configured backend
                email_subject = "Dib-u-dejinta Furahaaga Sirta ah | AQOONPLUS Academy"
                email_body = (
                    f"Asc {user.get_full_name() or user.username},\n\n"
                    f"Waxaa naga soo gaaray codsi ku saabsan dib-u-dejinta furahaaga sirta ah ee barta AQOONPLUS Academy.\n\n"
                    f"Fadlan guji link-gan hoose si aad u sameysato fure cusub:\n"
                    f"{reset_url}\n\n"
                    f"Haddii aadan adigu codsan dib-u-dejintan, fadlan iska indhatir email-kan. Furahaagu sidii ayuu ahaanayaa.\n\n"
                    f"Mahadsanid,\nKooxda Farsamada AQOONPLUS\n"
                )
                try:
                    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
                except Exception:
                    pass

                # Store direct link in session during DEBUG for instant testing
                request.session['debug_reset_url'] = reset_url
                request.session['reset_target_email'] = user.email
            else:
                request.session.pop('debug_reset_url', None)
                request.session['reset_target_email'] = identifier

            return redirect('password_reset_done')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_done_view(request):
    target_email = request.session.get('reset_target_email', '')
    debug_reset_url = request.session.get('debug_reset_url', None) if settings.DEBUG else None
    return render(request, 'accounts/password_reset_done.html', {
        'target_email': target_email,
        'debug_reset_url': debug_reset_url,
    })


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    is_valid = user is not None and default_token_generator.check_token(user, token)

    if not is_valid:
        return render(request, 'accounts/password_reset_confirm.html', {
            'is_valid': False,
        })

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            # Clean session debug helper
            request.session.pop('debug_reset_url', None)
            request.session.pop('reset_target_email', None)
            messages.success(request, "🎉 Furahaaga sirta ah si guul leh ayaa loo beddelay! Hadda waad gali kartaa.")
            return redirect('password_reset_complete')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/password_reset_confirm.html', {
        'is_valid': True,
        'form': form,
        'reset_user': user,
    })


def password_reset_complete_view(request):
    return render(request, 'accounts/password_reset_complete.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Furahaaga sirta ah si guul leh ayaa loo beddelay!")
            return redirect('profile')
        else:
            messages.error(request, "Fadlan sax khaladaadka hoos ku qoran.")
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def notifications_view(request):
    from .models import Notification
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "Dhammaan ogeysiisyada waxaa loo calaamadeeyay in la aqriyay.")
        return redirect('notifications')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark as read when visited
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
    })

