# Generated by Django 3.0.3 on 2020-02-18 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200215_1950'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
            ],
        ),
    ]