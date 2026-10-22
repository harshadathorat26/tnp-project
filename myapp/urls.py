from django.contrib import admin
from django.urls import path
from myapp import views 


urlpatterns = [
    path("",views.login_view, name='login_view'),
    path("register/", views.register_view, name="register"),
    # path("home",views.index,name='index'),
    path("application",views.application,name='application'),
    path('application/apply/<int:drive_id>/', views.apply_for_drive, name='apply_for_drive'),
    path("resume",views.resume,name='resume'),
    path("resume/delete/", views.delete_resume, name='delete_resume'),
    path("profile",views.profile,name='profile'),
    path("notification",views.notification,name='notification'),
    path("dashboard",views.dashboard, name ='dashboard'),
    path("logout",views.logout_view, name ='logout'),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
] 