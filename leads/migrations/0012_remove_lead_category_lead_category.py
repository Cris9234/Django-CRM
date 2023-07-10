# Generated by Django 4.2.2 on 2023-07-07 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0011_alter_category_organisation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='Category',
        ),
        migrations.AddField(
            model_name='lead',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads', to='leads.category'),
        ),
    ]
