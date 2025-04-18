# Generated by Django 3.2.16 on 2025-02-12 20:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0007_auto_20250212_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='username',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='useredit', to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='congratulation',
            name='text',
            field=models.TextField(verbose_name='Комментаий'),
        ),
    ]
