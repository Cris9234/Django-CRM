# Generated by Django 4.2.2 on 2023-07-03 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0003_alter_agent_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.userprofile'),
        ),
    ]