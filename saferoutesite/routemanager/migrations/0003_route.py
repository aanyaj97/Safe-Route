# Generated by Django 2.1.5 on 2019-03-09 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routemanager', '0002_auto_20190309_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('steps', models.CharField(max_length=100000)),
            ],
        ),
    ]
