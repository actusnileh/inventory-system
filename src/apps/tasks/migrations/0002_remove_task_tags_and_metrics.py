from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="task",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="task",
            name="estimated_hours",
        ),
        migrations.RemoveField(
            model_name="task",
            name="actual_hours",
        ),
        migrations.RemoveField(
            model_name="task",
            name="progress",
        ),
        migrations.DeleteModel(
            name="TaskTag",
        ),
        migrations.AlterField(
            model_name="taskactivity",
            name="action",
            field=models.CharField(
                choices=[
                    ("status", "Статус"),
                    ("comment", "Комментарий"),
                    ("checklist", "Чек-лист"),
                    ("attachment", "Файл"),
                ],
                max_length=32,
                verbose_name="Тип",
            ),
        ),
    ]
