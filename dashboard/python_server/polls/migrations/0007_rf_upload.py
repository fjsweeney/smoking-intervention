# Generated by Django 3.0 on 2020-02-07 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_clusterfileupload_uploaddate'),
    ]

    operations = [
        migrations.CreateModel(
            name='RF_Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participantFolder', models.FileField(upload_to='')),
                ('uploadDate', models.DateTimeField(auto_now_add=True)),
                ('ownerID', models.IntegerField()),
            ],
        ),
    ]
