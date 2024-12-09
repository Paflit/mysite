# Generated by Django 5.0.4 on 2024-04-16 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100)),
                ('job_title', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('score', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
    ]