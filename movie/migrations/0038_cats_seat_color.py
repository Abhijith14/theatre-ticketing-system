# Generated by Django 3.2.9 on 2021-11-27 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0037_cats_seat_seats_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='cats_seat',
            name='color',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
