from applications.models import Application, Job, User
from applications.serializers import UserSerializer
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from files.models import File
from files.serializers import FileSerializer
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .models import Group, GroupMember, GroupMessage
from .serializers import (
    GroupCreateInputSerializer,
    GroupMessageCreateInputSerializer,
    GroupMessageListInputSerializer,
    GroupMessagePartialUpdateInputSerializer,
    GroupMessageSerializer,
    GroupPartialUpdateInputSerializer,
)
from .utils import check_new_ids


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # POST -> groups/
    def create(self, request):
        # Input validation
        # Already ensures that members (employee/employer) "belong" to the job
        input_serializer = GroupCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data

        # Make sure that request user is part of the member list
        user_ids = validated_data["userIds"]
        if request.user.id not in user_ids:
            return HttpResponse(
                "Group creator is not present in member list.", status=400
            )

        # Create the group
        bio = validated_data["bio"]
        job_id = validated_data["jobId"]
        job = Job.objects.get(job_id=job_id)
        new_group = Group.objects.create(bio=bio, creator_id=request.user, job_id=job)

        # Create the group members
        # First, make the creator an admin member
        GroupMember.objects.create(
            user_id=request.user, group_id=new_group, role="Admin"
        )

        # Then, make the other members a normal member
        user_ids.remove(request.user.id)
        for user_id in user_ids:
            associated_user = User.objects.get(id=user_id)
            GroupMember.objects.create(
                user_id=associated_user,
                group_id=new_group,
                role="Member",
            )

        return HttpResponse(
            f"Successfully created group with group_id: {new_group.group_id}.",
            status=200,
        )

    # PATCH -> groups/:group_id
    def partial_update(self, request, pk=None):
        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=pk)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Check if user is a group admin
        is_admin = False
        try:
            member = GroupMember.objects.get(user_id=request.user, group_id=group)
            if member.role == "Admin":
                is_admin = True
        except GroupMember.DoesNotExist:
            pass

        if not is_admin:
            return HttpResponse("User must be a group admin.", status=400)

        # Input validation
        # We still need to compare the four lists against existing members of the group
        # Additionally, for add_ids, need to ensure that ids "belong" to the job, and hence the group
        input_serializer = GroupPartialUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data

        # Useful information
        existing_user_ids = set(
            GroupMember.objects.filter(group_id=group).values_list("user_id", flat=True)
        )

        # Update bio, if provided
        bio = validated_data.get("bio")
        if bio:
            group.bio = bio
            group.save()

        # Add new members, if provided
        add_ids = validated_data.get("addIds")
        if add_ids:
            # Ensure no existence
            for add_id in add_ids:
                if add_id in existing_user_ids:
                    return HttpResponse(
                        "User to be added already exists in the group.", status=400
                    )

            # Ensure valid add_ids
            try:
                check_new_ids(add_ids, group.job_id)
            except Exception as e:
                return HttpResponse(f"Failed to add new members: {e}.", status=400)

            # Safe to add
            for add_id in add_ids:
                associated_user = User.objects.get(id=add_id)
                GroupMember.objects.create(
                    user_id=associated_user,
                    group_id=group,
                    role="Member",
                )

        # Remove existing members, if provided
        remove_ids = validated_data.get("removeIds")
        if remove_ids:
            # Ensure existence
            for remove_id in remove_ids:
                if remove_id not in existing_user_ids:
                    return HttpResponse(
                        "User to be removed does not exist in the group.", status=400
                    )

            # Ensure that don't remove all members
            remaining_members = existing_user_ids.difference(remove_ids)
            if not remaining_members:
                return HttpResponse(
                    "Cannot remove all members of this group.", status=400
                )

            # Ensure that don't remove all admins
            admin_count = GroupMember.objects.filter(
                user_id__id__in=remaining_members, role="Admin"
            ).count()
            if admin_count < 1:
                return HttpResponse(
                    "Cannot remove all admins of this group.", status=400
                )

            # Safe to remove
            GroupMember.objects.filter(user_id__id__in=remove_ids).delete()

        # Make new admins, if provided
        make_admin_ids = validated_data.get("makeAdminIds")
        if make_admin_ids:
            # Ensure existence and member role
            for make_admin_id in make_admin_ids:
                if make_admin_id not in existing_user_ids:
                    return HttpResponse(
                        "User to be made admin does not exist in the group.",
                        status=400,
                    )
                member = GroupMember.objects.get(user_id=make_admin_id)
                if member.role == "Admin":
                    return HttpResponse(
                        "User to be made admin is already an admin.", status=400
                    )

            # Safe to make admin
            # Update mutates db directly, no need to save object back to db
            GroupMember.objects.filter(user_id__id__in=make_admin_ids).update(
                role="Admin"
            )

        # Strip existing admins, if provided
        strip_admin_ids = validated_data.get("stripAdminIds")
        if strip_admin_ids:
            # Ensure existence and admin role
            for strip_admin_id in strip_admin_ids:
                if strip_admin_id not in existing_user_ids:
                    return HttpResponse(
                        "User to be stripped from admin does not exist in the group.",
                        status=400,
                    )
                member = GroupMember.objects.get(user_id=make_admin_id)
                if member.role == "Member":
                    return HttpResponse(
                        "User to be stripped from admin is already not an admin.",
                        status=400,
                    )

            # Ensure that don't strip all admins
            admin_count = GroupMember.objects.filter(
                group_id=group, role="Admin"
            ).count()

            strip_count = GroupMember.objects.filter(
                group_id=group, user_id__id__in=strip_admin_ids, role="Admin"
            ).count()

            if admin_count - strip_count < 1:
                return HttpResponse(
                    "Cannot strip all admins of this group.", status=400
                )

            # Safe to strip admin
            GroupMember.objects.filter(user_id__id__in=strip_admin_ids).update(
                role="Member"
            )

        return HttpResponse("Successfully updated group details.", status=200)

    # Available members are employees who have applied for the job
    # But not in the group yet
    # GET -> groups/:group_id/available_members
    @action(detail=True, methods=["get"])
    def available_members(self, request, pk=None):
        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=pk)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Get current group members
        existing_user_ids = set(
            GroupMember.objects.filter(group_id=group).values_list("user_id", flat=True)
        )

        # Find available members
        available_members = (
            Application.objects.filter(job_id=group.job_id)
            .exclude(employee_id__in=existing_user_ids)
            .select_related("employee_id")
        )

        result = []
        for available_member in available_members:
            data = {
                "employee_id": available_member.employee_id.id,
                "name": f"{available_member.employee_id.first_name} {available_member.employee_id.last_name}",
                "jobId": group.job_id.job_id,
            }
            result.append(data)

        return JsonResponse(result, safe=False)


class GroupMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # POST -> group-messages/
    def create(self, request):
        # Input validation
        input_serializer = GroupMessageCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        content = validated_data.get("content")
        reply_to_id = validated_data.get("replyToId")
        group_id = validated_data["groupId"]

        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=group_id)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Check that user is part of the group
        try:
            GroupMember.objects.get(user_id=request.user, group_id=group)
        except GroupMember.DoesNotExist:
            return HttpResponse("User is not part of this group.", status=400)

        # Try to retrieve the reply to id
        # Ensure that its part of the group
        try:
            reply_to_message = GroupMessage.objects.get(
                message_id=reply_to_id, group_id=group
            )
        except GroupMessage.DoesNotExist:
            return HttpResponse("Reply to message does not exist.", status=400)

        # Construct the message
        new_message = GroupMessage(
            group_id=group,
            sender_id=request.user,
        )

        if content:
            new_message.content = content
        if reply_to_id:
            new_message.reply_to_id = reply_to_message
        new_message.save()

        return HttpResponse(
            f"Successfully created group message: {new_message.message_id}.", status=200
        )

    # GET multiple -> group-messages/
    def list(self, request):
        # Input validation
        input_serializer = GroupMessageListInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        group_id = validated_data["groupId"]
        since = validated_data["since"]

        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=group_id)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Check that user is part of the group
        try:
            GroupMember.objects.get(user_id=request.user, group_id=group)
        except GroupMember.DoesNotExist:
            return HttpResponse("User is not part of this group.", status=400)

        # Retrieve messages
        queryset = (
            GroupMessage.objects.prefetch_related("file_set")
            .select_related("sender_id", "reply_to_id")
            .filter(group_id=group)
            .order_by("created_at")
        )

        if since:
            messages = queryset.filter(
                date__gte=since,
            )

        # Construct response
        result = []
        for message in messages:
            message_serializer = GroupMessageSerializer(message)
            user_serializer = UserSerializer(message.sender_id)

            data = {"message": message_serializer.data, "sender": user_serializer.data}

            if message.reply_to_id:
                reply_to_message_serializer = GroupMessageSerializer(
                    message.reply_to_id
                )
                data["reply_to_message"] = reply_to_message_serializer.data
            else:
                data["reply_to_message"] = None

            if message.file_set.first():
                file_serializer = FileSerializer(message.file_set.first())
                data["file"] = file_serializer.data
            else:
                data["file"] = None

            result.append(data)

        return JsonResponse(result, safe=False)

    # PATCH -> group-messages/:message_id
    def partial_update(self, request, pk=None):
        # Input validation
        input_serializer = GroupMessagePartialUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.validated_data
        content = validated_data["content"]
        group_id = validated_data["groupId"]

        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=group_id)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Check that user is part of the group
        try:
            GroupMember.objects.get(user_id=request.user, group_id=group)
        except GroupMember.DoesNotExist:
            return HttpResponse("User is not part of this group.", status=400)

        # Try to retrieve the message record
        # Check that message is part of the group
        try:
            message = GroupMessage.objects.get(message_id=pk, group_id=group)
        except GroupMessage.DoesNotExist:
            return HttpResponse("Message does not exist.", status=400)

        # Check that user is sender of message
        if message.sender_id != request.user:
            return HttpResponse("Message is not sent by user.", status=400)

        # Modify the message
        message.content = content
        message.is_edited = True
        message.last_edited_at = timezone.now()
        message.save()

        return HttpResponse("Message succesfully edited.", status=200)

    # DELETE -> group-messages/:<message_id || group_id>
    def destroy(self, request, pk=None):
        # Extract relevant fields
        message_id = pk.split(" || ")[0]
        group_id = pk.split(" || ")[1]

        # Try to retrieve the group record
        try:
            group = Group.objects.get(group_id=group_id)
        except Group.DoesNotExist:
            return HttpResponse("Group not found.", status=400)

        # Check that user is part of the group
        try:
            GroupMember.objects.get(user_id=request.user, group_id=group)
        except GroupMember.DoesNotExist:
            return HttpResponse("User is not part of this group.", status=400)

        # Try to retrieve the message record
        # Check that message is part of the group
        try:
            message = GroupMessage.objects.get(message_id=message_id, group_id=group)
        except GroupMessage.DoesNotExist:
            return HttpResponse("Message does not exist.", status=400)

        # Check that user is sender of message
        if message.sender_id != request.user:
            return HttpResponse("Message is not sent by user.", status=400)

        # Soft delete the message
        message.content = "[This message has been deleted]"
        message.is_deleted = True
        message.save()

        # Try to retrieve the associated files (if exists)
        associated_files = File.objects.filter(associated_group_message=message)
        associated_files.delete()

        return HttpResponse("Message successfully deleted.", status=200)
