# Generated by Django 3.2.9 on 2021-11-19 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0034_auto_20211119_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='cats_seats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cats_name', models.CharField(max_length=1000, null=True)),
                ('seats_list', models.CharField(max_length=1000, null=True)),
                ('amount', models.IntegerField(null=True)),
            ],
        ),
    ]