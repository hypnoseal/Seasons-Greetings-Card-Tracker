# Generated by Django 3.1.4 on 2020-12-08 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card_tracker', '0002_auto_20201208_0450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipient',
            name='address',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
