# Generated by Django 3.2.16 on 2025-02-16 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_alter_congratulation_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='congratulation',
            options={'ordering': ('-created_at',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Коментарии'},
        ),
        migrations.AlterField(
            model_name='congratulation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
