# Generated by Django 2.2.5 on 2019-11-19 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='school_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(max_length=256)),
                ('school_rank', models.CharField(blank=True, max_length=256)),
                ('school_province', models.CharField(max_length=256)),
                ('school_city', models.CharField(max_length=256)),
                ('type_985', models.CharField(max_length=256)),
                ('type_211', models.CharField(max_length=256)),
                ('type_self', models.CharField(max_length=256)),
                ('school_belong', models.CharField(max_length=256)),
                ('school_type1', models.CharField(max_length=256)),
                ('school_type2', models.CharField(max_length=256)),
            ],
        ),
    ]
