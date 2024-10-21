
from django.contrib import admin
from django.urls import path
from GlassesShop_app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('glasses_order/<int:id>', views.GlassesOrderController, name='glasses_order_url'),
    path('', views.LensesController, name = 'main_url'),
    path('lens/<int:id>/', views.LensDescriptionController, name='lens_url'),
]
