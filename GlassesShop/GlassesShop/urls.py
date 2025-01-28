from django.contrib import admin
from django.urls import include, path
from GlassesShop_app import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('lenses/', views.LensesMethods.as_view(), name = 'lenses_url'),
    path('lens/<int:id>/', views.SingleLensMethods.as_view(), name = 'single_lens_url'),
    path('lens/<int:id>/addPicture/', views.LensAddPicture.as_view(), name = 'add_lens_picture_url'),
    path('lens/<int:id>/add/', views.AddLens.as_view(), name = 'add_lens_url'),

    path('glasses_orders/', views.GlassesOrdersMethods.as_view(), name = 'glasses_orders_url'),
    path('glasses_order/<int:id>/', views.GlassesOrderMethods.as_view(), name = 'glasses_order_url'),
    path('glasses_order/<int:id>/save/', views.SaveGlassesOrder.as_view(), name = 'save_glasses_order_url'),
    path('glasses_order/<int:id>/moderate/', views.ModerateGlassesOrder.as_view(), name = 'accept_glasses_order_url'),

    path('LensesInOrder/<int:glasses_order_id>/<int:lens_id>/', views.MToMMethods.as_view(), name = 'lenses_in_order_url'),

    path('User/', views.PersonalAccount.as_view(), name='UserLK_url'),
    path('User/register/', views.Registration.as_view(), name='UserRegistration_url'),
    path('User/login/', views.Authentication.as_view(), name='UserLogin_url'),
    path('User/logout/', views.Deauthorization.as_view(), name='UserLogout_url'),
    ]
