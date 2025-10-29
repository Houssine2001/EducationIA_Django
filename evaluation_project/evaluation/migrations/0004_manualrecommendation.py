# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0003_test_source_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualRecommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('message', models.TextField(verbose_name='Message de recommandation')),
                ('is_read', models.BooleanField(default=False, verbose_name="Lu par l'étudiant")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_recommendations', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_recommendations', to=settings.AUTH_USER_MODEL)),
                ('test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manual_recommendations', to='evaluation.test')),
            ],
            options={
                'verbose_name': 'Recommandation Manuelle',
                'verbose_name_plural': 'Recommandations Manuelles',
                'db_table': 'manual_recommendation',
                'ordering': ['-created_at'],
            },
        ),
    ]
