# Generated by Django 4.2.16 on 2024-11-19 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_importrecord_book_import_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='import_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='books.importrecord'),
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together={('id', 'import_record')},
        ),
    ]
