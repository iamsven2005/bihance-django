from django.db import models
from django.utils import timezone
from message.models import Message


# Predefined set of options for associated_type field
class AssociatedType(models.TextChoices):
    MESSAGE = 'Message'
    GROUP_MESSAGE = 'Group Message'


# References: 
# https://abenezer.org/blog/generic-foreign-key-check-constraint
# https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/#alternative-1-nullable-fields-on-source-table
class Files(models.Model):
    file_key = models.TextField(primary_key=True, db_column="fileKey")
    file_url = models.URLField(db_column='fileUrl')  
    file_name = models.TextField(db_column='fileName')  
    file_type = models.TextField(db_column='fileType')  
    file_size = models.IntegerField(db_column='fileSize')  
    created_at = models.DateTimeField(default=timezone.now, db_column='createdAt')  

    associated_type = models.TextField(choices=AssociatedType.choices, db_column="associatedType")    
    associated_message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.PROTECT, db_column="associatedMessage")
    associated_group_message = models.TextField(null=True, blank=True, db_column="associatedGroupMessage")
    # associated_group_message = models.ForeignKey(Groupmessage, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        db_table = 'files'
        indexes = [
            models.Index(fields=['associated_message']),
            models.Index(fields=['associated_group_message'])
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(
                        associated_type=AssociatedType.MESSAGE, 
                        associated_group_message__isnull=True,
                        associated_message__isnull=False,
                    ) |
                    models.Q(
                        associated_type=AssociatedType.GROUP_MESSAGE,
                        associated_message__isnull=True,
                        associated_group_message__isnull=False,
                    )
                ),
                name='%(app_label)s_%(class)s_only_one_associated_object',
            )
        ]


