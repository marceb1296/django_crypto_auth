# Generated by Django 4.0 on 2023-05-01 21:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_crypto', to='auth.user')),
            ],
            options={
                'swappable': 'crypto_auth.CryptoToken',
            },
        ),
    ]