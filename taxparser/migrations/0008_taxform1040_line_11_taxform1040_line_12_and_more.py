# Generated by Django 4.2.14 on 2024-07-23 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxparser', '0007_taxform1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxform1040',
            name='line_11',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxform1040',
            name='line_12',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxform1040',
            name='line_15',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxform1040',
            name='line_34',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxform1040',
            name='line_37',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxform1040',
            name='line_9',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=16),
            preserve_default=False,
        ),
    ]
