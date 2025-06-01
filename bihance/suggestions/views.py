from applications.models import User
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .models import Suggestion, SuggestionComment, SuggestionVote
from .serializers import (
    SuggestionCommentInputSerializer,
    SuggestionCreateInputSerializer,
    SuggestionLeaderboardInputSerializer,
    SuggestionListInputSerializer,
)
from .utils import (
    to_json_object_leaderboard,
    to_json_object_list,
    to_json_object_retrieve,
)


class SuggestionsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    base_queryset = (
        Suggestion.objects.select_related("author_id")
        # Annotate each suggestion with vote_count
        # Which is the number of votes, derived from "SuggestionVote" model
        .annotate(vote_count=Count("suggestionvote", distinct=True))
        # Annotate each suggestion with comment_count
        # Which is the number of comments, derived from "SuggestionComment" model
        .annotate(comment_count=Count("suggestioncomment", distinct=True))
    )

    # GET multiple -> suggestions/
    def list(self, request):
        # Input validation
        input_serializer = SuggestionListInputSerializer(data=request.query_params)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data

        # Define base queryset
        queryset = self.base_queryset.prefetch_related("suggestionvote_set")

        # Filter based on search
        search = validated_data.get("searchQuery")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # Filter based on sortBy
        sort_by = validated_data["sortBy"]
        match sort_by:
            case "newest":
                queryset = queryset.order_by("-created_at")
            case "oldest":
                queryset = queryset.order_by("created_at")
            case "most-voted":
                queryset = queryset.order_by("-vote_count")

            # An implemented suggestion has is_useful = True
            # Sorting by -is_useful shows the True ones first
            case "implemented":
                queryset = queryset.order_by("-is_useful", "-created_at")

            # A pending suggestion has is_useful = False
            # Sorting by is_useful shows the False ones first
            case "pending":
                queryset = queryset.order_by("is_useful", "-created_at")

        # Get JSON response
        result = []
        for suggestion in queryset:
            suggestion_json = to_json_object_list(suggestion)
            result.append(suggestion_json)

        return JsonResponse(result, safe=False)

    # GET single -> suggestions/:suggestion_id
    def retrieve(self, request, pk=None):
        # Try to retrieve the suggestion record
        try:
            suggestion = self.base_queryset.prefetch_related(
                "suggestionvote_set", "suggestioncomment_set"
            ).get(suggestion_id=pk)
        except Suggestion.DoesNotExist:
            return HttpResponse("Suggestion not found,", status=400)

        suggestion_json = to_json_object_retrieve(suggestion)
        return JsonResponse(suggestion_json)

    # POST -> suggestions/
    def create(self, request):
        # Input validation
        input_serializer = SuggestionCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data

        # Create the suggestion
        validated_data["author_id"] = request.user
        suggestion = Suggestion.objects.create(**validated_data)
        return HttpResponse(
            f"Suggestion created with {suggestion.suggestion_id}.", status=200
        )

    # POST -> suggestions/:suggestion_id/vote
    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        # Try to retrieve the suggestion record
        try:
            suggestion = self.base_queryset.get(suggestion_id=pk)
        except Suggestion.DoesNotExist:
            return HttpResponse("Suggestion not found,", status=400)

        # Check if vote already exists
        has_voted = False
        try:
            current_vote = SuggestionVote.objects.get(
                user_id=request.user, suggestion_id=suggestion
            )
            has_voted = True
        except SuggestionVote.DoesNotExist:
            pass

        # Conditional processing
        if has_voted:
            current_vote.delete()
            return HttpResponse("Vote successfully deleted.", status=200)
        else:
            SuggestionVote.objects.create(
                user_id=request.user, suggestion_id=suggestion
            )
            return HttpResponse("Vote successfully created", status=200)

    # POST -> suggestions/:suggestion_id/comment
    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        # Try to retrieve the suggestion record
        try:
            suggestion = self.base_queryset.get(suggestion_id=pk)
        except Suggestion.DoesNotExist:
            return HttpResponse("Suggestion not found,", status=400)

        # Input validation
        input_serializer = SuggestionCommentInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data

        # Create the comment
        content = validated_data["content"]
        SuggestionComment.objects.create(
            content=content, author_id=request.user, suggestion_id=suggestion
        )
        return HttpResponse("Comment successfully created.", status=200)

    # POST -> suggestions/:suggestion_id/mark_implemented
    @action(detail=True, methods=["post"])
    def mark_implemented(self, request, pk=None):
        # Try to retrieve the suggestion record
        try:
            suggestion = self.base_queryset.get(suggestion_id=pk)
        except Suggestion.DoesNotExist:
            return HttpResponse("Suggestion not found.", status=400)

        # Check if user is admin
        if request.user.role != "Admin":
            return HttpResponse("User must be an admin.", status=400)

        # Mark suggestion
        suggestion.is_useful = True
        suggestion.save()

        return HttpResponse(
            "Successfully marked suggestion as implemented.", status=200
        )

    # GET -> suggestions/leaderboards
    @action(detail=False, methods=["get"])
    def leaderboards(self, request):
        # Input validation
        input_serializer = SuggestionLeaderboardInputSerializer(
            data=request.query_params
        )
        if not input_serializer.is_valid():
            return HttpResponse(input_serializer.errors, status=400)

        validated_data = input_serializer.data

        # Define base queryset
        queryset = User.objects.all()

        # Filter based on search
        search = validated_data.get("searchQuery")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search)
            )

        # Filter based on sortBy
        sort_by = validated_data["sortBy"]
        match sort_by:
            case "most-implemented":
                queryset = queryset.annotate(
                    implemented_count=Count(
                        "suggestion", filter=Q(suggestion__is_useful=True)
                    )
                ).order_by("-implemented_count")
            case "most-votes":
                queryset = queryset.annotate(
                    vote_count=Count("suggestionvote")
                ).order_by("-vote_count")
            case "newest-member":
                queryset = queryset.order_by("-created_at")

        result = []
        for user in queryset:
            user_json = to_json_object_leaderboard(user)
            result.append(user_json)

        return JsonResponse(result, safe=False)
