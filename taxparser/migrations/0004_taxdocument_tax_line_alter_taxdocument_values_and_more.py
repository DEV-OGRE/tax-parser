# Generated by Django 4.2.14 on 2024-07-23 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxparser', '0003_remove_taxdocumentvalues_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxdocument',
            name='tax_line',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='taxdocument',
            name='values',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='taxdocumentvalues',
            name='key_locations',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='taxdocumentvalues',
            name='raw_ocr',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='taxdocumentvalues',
            name='values',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
