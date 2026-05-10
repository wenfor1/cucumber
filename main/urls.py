from django.urls import path
from django.conf.urls.static import static
from cashflow import settings
from . import views
from .views import report_api

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('createPlan/', views.add_expense, name='createPlan'),
    path('createBudget/', views.createBudget, name='createBudget'),
    path('chart/', views.chart, name='chart'),
    path('analytics/', views.analytics, name='analytics'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('api/reports/', report_api, name='report_api'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('save-card/', views.save_card, name='save_card'),
    path('get-cards/', views.get_user_cards, name='get_cards'),
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)