"""
URL configuration for MiniProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from Home.views import (home, Admin_Login, Admin_Panel, login_page, signup_page, logout_page, download_complaints_pdf, view_complaint, edit_complaint, delete_complaint)

urlpatterns = [
    path('', login_page, name='login_page'),
    path('logout/', logout_page, name='logout_page'),
    path('signup/', signup_page, name='signup_page'),
    path('home/', home, name='home'),
    path('AdminLogin/', Admin_Login, name='Admin_Login'),
    path('AdminPanel/', Admin_Panel, name='Admin_Panel'),
    path('download-pdf/', download_complaints_pdf, name='download_complaints_pdf'),

    # Complaint actions for users
    path('complaints/<int:complaint_id>/', view_complaint, name='view_complaint'),
    path('complaints/<int:complaint_id>/edit/', edit_complaint, name='edit_complaint'),
    path('complaints/<int:complaint_id>/delete/', delete_complaint, name='delete_complaint'),

    path('admin/', admin.site.urls),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
