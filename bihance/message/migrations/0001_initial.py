# Generated by Django 5.2 on 2025-05-21 14:51

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applications", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "message_id",
                    models.TextField(
                        db_column="msgId",
                        default=uuid.uuid4,
                        max_length=36,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("content", models.TextField()),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_edited", models.BooleanField(db_column="isEdited", default=False)),
                (
                    "is_deleted",
                    models.BooleanField(db_column="isDeleted", default=False),
                ),
                (
                    "last_edited_at",
                    models.DateTimeField(
                        blank=True, db_column="lastEditedAt", null=True
                    ),
                ),
                (
                    "application_id",
                    models.ForeignKey(
                        db_column="matchId",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="applications.application",
                    ),
                ),
                (
                    "reply_to_id",
                    models.ForeignKey(
                        blank=True,
                        db_column="replyToId",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="message.message",
                    ),
                ),
                (
                    "sender_id",
                    models.ForeignKey(
                        db_column="senderId",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "Message",
                "indexes": [
                    models.Index(
                        fields=["application_id"], name="Message_matchId_cbac6c_idx"
                    ),
                    models.Index(
                        fields=["sender_id"], name="Message_senderI_66e146_idx"
                    ),
                    models.Index(
                        fields=["reply_to_id"], name="Message_replyTo_d5d699_idx"
                    ),
                ],
            },
        ),
    ]
