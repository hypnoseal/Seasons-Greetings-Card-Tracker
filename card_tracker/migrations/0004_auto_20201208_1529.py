# Generated by Django 3.1.4 on 2020-12-08 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card_tracker', '0003_auto_20201208_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homebase',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
