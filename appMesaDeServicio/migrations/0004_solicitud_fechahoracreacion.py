# Generated by Django 4.2.13 on 2024-05-29 16:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('appMesaDeServicio', '0003_caso_fechahoracreacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='fechaHoraCreacion',
            field=models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de la solicitud', default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
