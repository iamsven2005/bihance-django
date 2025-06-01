from functools import reduce
from operator import or_

from applications.models import Job, User
from companies.models import EmployerProfile
from django.db import models
from django.utils import timezone
from message.models import Message


class AssociatedType(models.TextChoices):
    MESSAGE = "Message"
    GROUP_MESSAGE = "Group Message"
    USER = "User"
    JOB = "Job"
    COMPANY = "Company"


atype_to_condition_map = {
    AssociatedType.MESSAGE: "associated_message__isnull",
    AssociatedType.GROUP_MESSAGE: "associated_group_message__isnull",
    AssociatedType.USER: "associated_user__isnull",
    AssociatedType.JOB: "associated_job__isnull",
    AssociatedType.COMPANY: "associated_company__isnull",
}


# Each Q object represents a criteria
# The smaller conditions, that make up the criteria
# Is given as a collection of key-value pairs
def check_associated_objects():
    q_objects_list = []

    for atype in AssociatedType.values:
        condition_dict = create_condition_dictionary(atype)
        q_object = models.Q(**condition_dict)
        q_objects_list.append(q_object)

    # Reduce over all Q objects, using OR to join them
    # Obtain a single Q object (that basically says, only ONE Q object needs to be satisfied)
    return reduce(or_, q_objects_list)


def create_condition_dictionary(atype):
    result = {}
    result["associated_type"] = atype

    # Identify the false isnull condition
    # All other isnull conditions will be true
    false_condition = atype_to_condition_map[atype]
    conditions = atype_to_condition_map.values()

    for condition in conditions:
        if condition == false_condition:
            result[condition] = False
        else:
            result[condition] = True

    return result


# References:
# https://abenezer.org/blog/generic-foreign-key-check-constraint
# https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/#alternative-1-nullable-fields-on-source-table
class File(models.Model):
    file_key = models.TextField(primary_key=True, db_column="fileKey")
    file_url = models.URLField(db_column="fileUrl")
    file_name = models.TextField(db_column="fileName")
    file_type = models.TextField(db_column="fileType")
    file_size = models.IntegerField(db_column="fileSize")
    created_at = models.DateTimeField(default=timezone.now, db_column="createdAt")

    associated_type = models.TextField(
        choices=AssociatedType.choices, db_column="associatedType"
    )
    associated_message = models.ForeignKey(
        Message,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_column="associatedMessage",
    )
    # associated_group_message = models.ForeignKey(Groupmessage, null=True, blank=True, on_delete=models.PROTECT) [IN FUTURE]
    associated_group_message = models.TextField(
        null=True, blank=True, db_column="associatedGroupMessage"
    )

    associated_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_column="associatedUser",
    )
    associated_job = models.ForeignKey(
        Job, null=True, blank=True, on_delete=models.PROTECT, db_column="associatedJob"
    )
    associated_company = models.ForeignKey(
        EmployerProfile,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_column="associatedCompany",
    )

    class Meta:
        db_table = "File"
        indexes = [
            models.Index(fields=["associated_message"]),
            models.Index(fields=["associated_group_message"]),
            models.Index(fields=["associated_user"]),
            models.Index(fields=["associated_job"]),
            models.Index(fields=["associated_company"]),
        ]
        constraints = [
            # Row level check constraint
            models.CheckConstraint(
                check=check_associated_objects(),
                name="%(app_label)s_%(class)s_only_one_associated_object",
            )
        ]
