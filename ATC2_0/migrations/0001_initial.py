# Generated by Django 2.2.6 on 2019-11-21 20:46

from django.db import migrations, models
import django.db.models.deletion
import django_prometheus.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            bases=(models.Model, django_prometheus.models.ExportModelOperationsMixin('Airline')),
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('airlines', models.ManyToManyField(to='ATC2_0.Airline')),
            ],
            bases=(models.Model, django_prometheus.models.ExportModelOperationsMixin('Airport')),
        ),
        migrations.CreateModel(
            name='Gate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('size', models.CharField(choices=[('SMALL', 'Small'), ('MEDIUM', 'Medium'), ('LARGE', 'Large')], default='SMALL', max_length=6)),
                ('airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ATC2_0.Airport')),
            ],
            bases=(models.Model, django_prometheus.models.ExportModelOperationsMixin('Gate')),
        ),
        migrations.CreateModel(
            name='Runway',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('size', models.CharField(choices=[('SMALL', 'Small'), ('MEDIUM', 'Medium'), ('LARGE', 'Large')], default='SMALL', max_length=6)),
                ('airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ATC2_0.Airport')),
            ],
            bases=(models.Model, django_prometheus.models.ExportModelOperationsMixin('Runway')),
        ),
        migrations.CreateModel(
            name='Plane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('size', models.CharField(choices=[('SMALL', 'Small'), ('MEDIUM', 'Medium'), ('LARGE', 'Large')], default='SMALL', max_length=6)),
                ('currentPassengerCount', models.IntegerField()),
                ('maxPassengerCount', models.IntegerField()),
                ('heading', models.FloatField(null=True)),
                ('speed', models.FloatField(null=True)),
                ('take_off_time', models.DateTimeField(null=True)),
                ('landing_time', models.DateTimeField(null=True)),
                ('arrive_at_gate_time', models.DateTimeField(null=True)),
                ('arrive_at_runway_time', models.DateTimeField(null=True)),
                ('airline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ATC2_0.Airline')),
                ('gate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ATC2_0.Gate')),
                ('land_airport', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='landing_airport', to='ATC2_0.Airport')),
                ('runway', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ATC2_0.Runway')),
                ('take_off_airport', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='take_off_airport', to='ATC2_0.Airport')),
            ],
            bases=(models.Model, django_prometheus.models.ExportModelOperationsMixin('Plane')),
        ),
    ]
