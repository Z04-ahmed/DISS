# Generated by Django 5.2 on 2025-06-09 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('yellow', 'Yellow'), ('black', 'Black'), ('white', 'White'), ('purple', 'Purple'), ('pink', 'Pink'), ('orange', 'Orange'), ('brown', 'Brown'), ('gray', 'Gray'), ('navy', 'Navy'), ('beige', 'Beige'), ('gold', 'Gold'), ('silver', 'Silver')], max_length=50, null=True),
        ),
    ]
