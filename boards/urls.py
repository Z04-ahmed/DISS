from django.urls import path
from . import views

urlpatterns = [
    path('', views.boards_list, name='boards'),
    path('create/', views.create_board, name='create_board'),
    path('<int:board_id>/delete/', views.delete_board, name='delete_board'),
    path('<int:board_id>/edit/', views.edit_board, name='edit_board'),
    path('<int:pk>/', views.board_detail, name='board_detail'),
    path('add-product/', views.add_product_to_board, name='add_product_to_board'),
]
