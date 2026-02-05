from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="task",
            constraint=models.UniqueConstraint(
                fields=("user", "target_date", "title"),
                name="unique_task_per_user_per_day",
            ),
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("user", "target_date"),
                name="unique_notification_per_user_per_day",
            ),
        ),
    ]
