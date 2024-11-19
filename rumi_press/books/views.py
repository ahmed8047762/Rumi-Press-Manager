from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, DateTimeField, Avg
from django.db.models.functions import TruncMonth
from .models import Category, Book, ImportRecord
from .serializers import CategorySerializer, BookSerializer
from django.contrib import messages
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import json
import os
from django.db.models import Q
from django.utils import timezone
from django.db import models, transaction

def dashboard(request):
    import_id = request.GET.get('import_id')
    selected_import = None
    
    # Get all imports for the sidebar
    imports = ImportRecord.objects.all().order_by('-created_at')
    
    # Base queryset
    books = Book.objects.all()
    
    # Filter by import record if selected
    if import_id:
        selected_import = get_object_or_404(ImportRecord, id=import_id)
        books = books.filter(import_record=selected_import)
    
    # Calculate total books and expenses
    total_books = books.count()
    total_expense = books.aggregate(total=Sum('distribution_expense'))['total'] or 0
    
    # Get category distribution
    categories = Category.objects.filter(books__in=books).distinct()
    category_stats = []
    for category in categories:
        category_books = books.filter(category=category)
        category_stats.append({
            'name': category.name,
            'book_count': category_books.count(),
            'total_expense': category_books.aggregate(total=Sum('distribution_expense'))['total'] or 0
        })
    
    # Sort categories by book count
    category_stats.sort(key=lambda x: x['book_count'], reverse=True)
    
    # Calculate expense trends
    today = timezone.now().date()
    
    # Daily trend (last 7 days)
    week_ago = today - timedelta(days=7)
    daily_trend = []
    for i in range(7):
        date = week_ago + timedelta(days=i)
        daily_books = books.filter(created_at__date=date)
        daily_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'expense': daily_books.aggregate(total=Sum('distribution_expense'))['total'] or 0,
            'book_count': daily_books.count()
        })
    
    # Monthly trend (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_trend = []
    current_date = six_months_ago
    while current_date <= today:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1)
        
        monthly_books = books.filter(created_at__date__gte=month_start, created_at__date__lt=month_end)
        monthly_trend.append({
            'month': month_start.strftime('%B %Y'),
            'expense': monthly_books.aggregate(total=Sum('distribution_expense'))['total'] or 0,
            'book_count': monthly_books.count()
        })
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Category expense distribution over time
    category_trend = []
    for category in categories:
        monthly_data = []
        for month_data in monthly_trend:
            month_start = datetime.strptime(month_data['month'], '%B %Y').date().replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            
            category_monthly_expense = books.filter(
                category=category,
                created_at__date__gte=month_start,
                created_at__date__lt=month_end
            ).aggregate(total=Sum('distribution_expense'))['total'] or 0
            
            monthly_data.append(category_monthly_expense)
        
        category_trend.append({
            'category': category.name,
            'data': monthly_data
        })
    
    context = {
        'show_sidebar': True,
        'total_books': total_books,
        'total_expense': total_expense,
        'category_stats': category_stats,
        'daily_trend': daily_trend,
        'monthly_trend': monthly_trend,
        'category_trend': category_trend,
        'import_history': imports,
        'selected_import': selected_import,
        'no_imports': not imports.exists()
    }
    
    return render(request, 'books/dashboard.html', context)

def book_list(request):
    import_id = request.GET.get('import_id')
    selected_import = None
    
    # Get all imports for the sidebar
    imports = ImportRecord.objects.all().order_by('-created_at')
    
    # Base queryset
    books = Book.objects.all()
    
    # Filter by import record if selected
    if import_id:
        selected_import = get_object_or_404(ImportRecord, id=import_id)
        books = books.filter(import_record=selected_import)
    
    # Get statistics for the filtered books
    total_books = books.count()
    total_expense = books.aggregate(total=Sum('distribution_expense'))['total'] or 0
    categories = Category.objects.filter(books__in=books).distinct()
    category_stats = []
    for category in categories:
        category_books = books.filter(category=category)
        category_stats.append({
            'name': category.name,
            'book_count': category_books.count(),
            'total_expense': category_books.aggregate(total=Sum('distribution_expense'))['total'] or 0
        })
    
    # Sort categories by book count
    category_stats.sort(key=lambda x: x['book_count'], reverse=True)
    
    # Get the latest books for the filtered set
    latest_books = books.order_by('-created_at')[:5]
    
    context = {
        'show_sidebar': True,
        'total_books': total_books,
        'total_expense': total_expense,
        'category_stats': category_stats,
        'latest_books': latest_books,
        'import_history': imports,
        'selected_import': selected_import,
        'no_imports': not imports.exists()
    }
    return render(request, 'books/book_list.html', context)

class BookCreateView(CreateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['id', 'title', 'subtitle', 'authors', 'publisher', 'published_date', 'category', 'distribution_expense']
    success_url = reverse_lazy('books:book_list')

class BookUpdateView(UpdateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'subtitle', 'authors', 'publisher', 'published_date', 'category', 'distribution_expense']
    success_url = reverse_lazy('books:book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')

# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'books/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = Category
    template_name = 'books/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('books:category_list')

class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'books/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('books:category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'books/category_confirm_delete.html'
    success_url = reverse_lazy('books:category_list')

# Report Views
def expense_report(request):
    categories = Category.objects.all()
    for category in categories:
        category.total_expenses = category.books.aggregate(
            total=Sum('distribution_expense'))['total'] or 0
        category.book_count = category.books.count()
    return render(request, 'books/expense_report.html', {'categories': categories})

def distribution_analysis(request):
    return render(request, 'books/distribution_analysis.html')

def trend_analysis(request):
    return render(request, 'books/trend_analysis.html')

def clean_isbn(isbn):
    """Clean and standardize ISBN/ID format."""
    if not isbn:
        return None
    
    # Convert to string and remove any whitespace
    isbn = str(isbn).strip()
    
    # Handle special cases (library IDs)
    if any(prefix in isbn for prefix in ['OSU:', 'UOM:', 'UVA:', 'UCSD:', 'UCSC:']):
        return isbn
    
    # Remove any non-alphanumeric characters
    isbn = ''.join(c for c in isbn if c.isalnum())
    
    # If it's a numeric ISBN, ensure it's properly formatted
    if isbn.isdigit():
        # Handle ISBN-13
        if len(isbn) >= 13:
            return isbn[:13]
        # Handle ISBN-10
        elif len(isbn) >= 10:
            return isbn[:10]
    
    return isbn

def import_books(request):
    import_id = request.GET.get('import_id')
    selected_import = None
    if import_id:
        selected_import = get_object_or_404(ImportRecord, id=import_id)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        filename = excel_file.name
        
        try:
            # Read Excel file and print its structure
            df = pd.read_excel(excel_file)
            print("Excel columns:", df.columns.tolist())
            print("First row:", df.iloc[0].to_dict())
            
            # Map column names to expected names
            column_mapping = {
                'id': 'isbn',  # Map 'id' column to 'isbn'
                'ID': 'isbn',  # Also try uppercase
                'ISBN': 'isbn',  # Also try ISBN
                'isbn': 'isbn'  # Keep isbn as is
            }
            
            # Find the ISBN column
            isbn_column = None
            for col in df.columns:
                if col in column_mapping:
                    isbn_column = col
                    break
                    
            if not isbn_column:
                raise ValueError("Could not find ISBN column. Expected one of: id, ID, ISBN, isbn")
                
            # Rename the column to 'isbn'
            df = df.rename(columns={isbn_column: 'isbn'})
            
            # Start a transaction to ensure data consistency
            with transaction.atomic():
                # Create import record first
                import_record = ImportRecord.objects.create(
                    filename=filename,
                    book_count=len(df)
                )
                print(f"Created import record: {import_record.id}")
                
                # Create books in bulk for better performance
                books_to_create = []
                categories_cache = {}
                seen_isbns = set()  # Track unique ISBNs within this import only
                skipped_count = 0
                
                for index, row in df.iterrows():
                    try:
                        # Clean and validate ISBN
                        isbn = clean_isbn(str(row['isbn']))
                        if not isbn:
                            print(f"Warning: Empty or invalid ISBN in row {index + 1}, skipping")
                            skipped_count += 1
                            continue
                            
                        # Skip duplicate ISBNs within this import only
                        if isbn in seen_isbns:
                            print(f"Warning: Duplicate ISBN {isbn} in row {index + 1} of this import, skipping")
                            skipped_count += 1
                            continue
                        seen_isbns.add(isbn)
                        
                        # Get or create category using cache
                        category_name = str(row['category']).strip()
                        if not category_name:
                            print(f"Warning: Empty category in row {index + 1}, using 'Uncategorized'")
                            category_name = 'Uncategorized'
                            
                        if category_name not in categories_cache:
                            category, _ = Category.objects.get_or_create(
                                name=category_name,
                                defaults={'description': ''}
                            )
                            categories_cache[category_name] = category
                        category = categories_cache[category_name]
                        
                        # Parse date with timezone awareness
                        try:
                            published_date = pd.to_datetime(row['published_date']).date()
                        except:
                            published_date = timezone.now().date()
                            print(f"Warning: Invalid date in row {index + 1}, using today's date")
                        
                        # Validate required string fields
                        for field in ['title', 'authors', 'publisher']:
                            if not str(row[field]).strip():
                                raise ValueError(f"Empty {field} in row {index + 1}")
                        
                        # Validate and convert distribution expense
                        try:
                            distribution_expense = float(row['distribution_expense'])
                            if distribution_expense < 0:
                                distribution_expense = 0
                                print(f"Warning: Negative expense in row {index + 1}, setting to 0")
                        except:
                            distribution_expense = 0
                            print(f"Warning: Invalid expense in row {index + 1}, setting to 0")
                        
                        # Create book instance
                        book = Book(
                            isbn=isbn,
                            title=str(row['title']).strip(),
                            subtitle=str(row.get('subtitle', '')).strip(),
                            authors=str(row['authors']).strip(),
                            publisher=str(row['publisher']).strip(),
                            published_date=published_date,
                            category=category,
                            distribution_expense=distribution_expense,
                            import_record=import_record,
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                        )
                        books_to_create.append(book)
                        if len(books_to_create) % 1000 == 0:
                            print(f"Processed {len(books_to_create)} valid books...")
                        
                    except Exception as row_error:
                        print(f"Warning: Error in row {index + 1}: {str(row_error)}, skipping")
                        skipped_count += 1
                        continue
                
                print(f"\nSummary before import:")
                print(f"- Total rows in Excel: {len(df)}")
                print(f"- Valid books to create: {len(books_to_create)}")
                print(f"- Skipped rows: {skipped_count}")
                print(f"- Unique categories: {len(categories_cache)}")
                
                # Create books in smaller batches to avoid memory issues
                batch_size = 500
                total_created = 0
                for i in range(0, len(books_to_create), batch_size):
                    batch = books_to_create[i:i + batch_size]
                    Book.objects.bulk_create(batch)
                    total_created += len(batch)
                    print(f"Created batch of {len(batch)} books. Total: {total_created}")
                
                # Update the final book count
                import_record.book_count = total_created
                import_record.save()
                
                print(f"\nImport completed:")
                print(f"- Successfully created {total_created} books")
                print(f"- Skipped {skipped_count} invalid/duplicate entries")
            
            messages.success(
                request,
                f'Successfully imported {total_created} books from {filename} '
                f'({skipped_count} entries skipped)'
            )
            return redirect('books:book_list')
            
        except Exception as e:
            print(f"Import error: {str(e)}")
            if 'import_record' in locals():
                import_record.delete()
            messages.error(request, f'Error importing file: {str(e)}')
            return redirect('books:import_books')
    
    imports = ImportRecord.objects.all().order_by('-created_at')
    context = {
        'show_sidebar': True,
        'import_history': imports,
        'selected_import': selected_import,
        'no_imports': not imports.exists()
    }
    return render(request, 'books/import.html', context)

def update_import(request, pk):
    import_record = get_object_or_404(ImportRecord, id=pk)
    if request.method == 'POST':
        try:
            # Get the file from the request
            file = request.FILES.get('file')
            if not file:
                messages.error(request, 'No file was uploaded.')
                return redirect('books:book_list')

            # Read the Excel file
            df = pd.read_excel(file)

            # Start a transaction
            with transaction.atomic():
                # Delete existing books for this import
                Book.objects.filter(import_record=import_record).delete()

                # Process each row in the dataframe
                for _, row in df.iterrows():
                    # Clean and standardize ISBN
                    isbn = clean_isbn(str(row.get('ISBN', '')))
                    
                    # Get or create the category
                    category_name = row.get('Category', 'Uncategorized')
                    category, _ = Category.objects.get_or_create(name=category_name)
                    
                    # Create the book
                    Book.objects.create(
                        id=isbn,
                        title=row.get('Title', ''),
                        subtitle=row.get('Subtitle', ''),
                        authors=row.get('Authors', ''),
                        publisher=row.get('Publisher', ''),
                        published_date=row.get('Published Date'),
                        category=category,
                        distribution_expense=row.get('Distribution Expense', 0.0),
                        import_record=import_record
                    )

                # Update import record
                import_record.filename = file.name
                import_record.save()

            messages.success(request, f'Successfully updated import: {file.name}')
            return redirect('books:book_list')

        except Exception as e:
            messages.error(request, f'Error updating import: {str(e)}')
            return redirect('books:book_list')

    return render(request, 'books/import_update.html', {'import_record': import_record})

def delete_import(request, pk):
    import_record = get_object_or_404(ImportRecord, id=pk)
    try:
        # Start a transaction to ensure data consistency
        with transaction.atomic():
            # Delete all books associated with this import
            Book.objects.filter(import_record_id=pk).delete()
            # Then delete the import record
            import_record.delete()
        messages.success(request, f'Successfully deleted import: {import_record.filename}')
    except Exception as e:
        messages.error(request, f'Error deleting import: {str(e)}')
    return redirect('books:book_list')  # Add this line to redirect after deletion

# API ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        category = self.get_object()
        total_expenses = category.books.aggregate(
            total=Sum('distribution_expense'))['total'] or 0
        return Response({
            'category': category.name,
            'total_expenses': total_expenses,
            'book_count': category.books.count()
        })

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset
