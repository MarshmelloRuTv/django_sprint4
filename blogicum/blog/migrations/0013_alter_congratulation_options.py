# Generated by Django 3.2.16 on 2025-02-17 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20250216_2208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='congratulation',
            options={'ordering': ('created_at',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Коментарии'},
        ),
    ]
