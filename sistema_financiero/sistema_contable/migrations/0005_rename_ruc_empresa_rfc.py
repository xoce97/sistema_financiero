# Generated by Django 5.2.2 on 2025-06-09 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_contable', '0004_alter_cuentacontable_tipo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='empresa',
            old_name='ruc',
            new_name='rfc',
        ),
    ]
