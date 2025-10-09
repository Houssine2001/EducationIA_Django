# Generated migration for adding source_type field to Test model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0002_userprofile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='source_type',
            field=models.CharField(
                choices=[
                    ('manual', 'Test Manuel (Professeur)'),
                    ('ai_generated', 'Test Généré par IA')
                ],
                default='manual',
                help_text='Origine du test',
                max_length=20
            ),
        ),
    ]
