from django.urls import path
from .views import book_list, import_books, dashboard, update_import, delete_import

app_name = 'books'

urlpatterns = [
    path('', book_list, name='book_list'),
    path('import/', import_books, name='import_books'),
    path('dashboard/', dashboard, name='dashboard'),
    path('import/<int:pk>/update/', update_import, name='update_import'),
    path('import/<int:pk>/delete/', delete_import, name='delete_import'),
]
