# Generated by Django 5.1.1 on 2024-09-30 12:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=10)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('version_id', models.CharField(max_length=100, unique=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataSleuthApp.agent')),
            ],
        ),
        migrations.CreateModel(
            name='LeakDetectionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
                ('unauthorized_location', models.CharField(max_length=255)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataSleuthApp.file')),
            ],
        ),
    ]
