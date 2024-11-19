from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class ImportRecord(models.Model):
    filename = models.CharField(max_length=255)
    book_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.filename} ({self.book_count} books)"

    class Meta:
        ordering = ['-created_at']

class Book(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing ID
    isbn = models.CharField(max_length=20)  # ISBN identifier
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    authors = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    published_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    distribution_expense = models.DecimalField(max_digits=10, decimal_places=2)
    import_record = models.ForeignKey(
        ImportRecord,
        on_delete=models.SET_NULL,  # Don't delete books if import record is deleted
        related_name='books',
        null=True,  # Allow null for existing records
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ['isbn', 'import_record']  # Allow same ISBN in different imports
