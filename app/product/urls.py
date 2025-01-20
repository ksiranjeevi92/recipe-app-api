from django.urls import path
from product import views

urlpatterns = [
    path("products/", views.get_products, name='products'),
    path("upload-images/", views.upload_product_images, name="upload_product_images"),
    path("new/", views.new_product, name='new_product'),
    path("product/<str:pk>/", views.get_product, name='get_product_details'),
    path("product/<str:pk>/update/", views.update_product, name='update_product'),
    path("product/<str:pk>/delete/", views.delete_product, name='delete_product')
]