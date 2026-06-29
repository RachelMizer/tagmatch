from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0007_alter_profile_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="time_format",
            field=models.CharField(
                choices=[("12hr", "12-hour (AM/PM)"), ("24hr", "24-hour")],
                default="12hr",
                max_length=4,
            ),
        ),
    ]
