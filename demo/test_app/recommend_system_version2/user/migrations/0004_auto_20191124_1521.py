# Generated by Django 2.2.5 on 2019-11-24 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20191124_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='province',
            field=models.CharField(choices=[('广东', '广东')], default='广东', max_length=64),
        ),
        migrations.AlterField(
            model_name='user',
            name='sex',
            field=models.CharField(choices=[('男', '男'), ('女', '女')], default='男', max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='subject',
            field=models.CharField(choices=[('理科', '理科'), ('文科', '文科')], default='理科', max_length=64),
        ),
    ]
