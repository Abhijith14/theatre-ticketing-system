# Generated by Django 3.1.4 on 2021-08-17 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0020_movie_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='time',
            field=models.CharField(choices=[('9', '9:00 AM'), ('down', 'Down vote')], max_length=200, null=True),
        ),
    ]
