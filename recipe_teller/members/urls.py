from django.urls import path,include
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.members, name='home'),
    path('accounts/', include('django.contrib.auth.urls')), 

    path('members/', views.members, name='members'), 
    path('submit_recipe/', views.submit_recipe, name='submit_recipe'),  # Named URL -
    path('success/', views.success, name='success'),  
    path('recipe_teller/', views.recipe_teller, name='recipe_teller'),
    path('admin/', admin.site.urls),
    #other routes
    path('save_favourite/<int:recipe_id>/', views.save_favourite, name='save_favourite'),
    path('favourites/', views.view_favourites, name='view_favourites'),

]






