"""
Views for /tag/ and /tag/<pk>/
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.db import IntegrityError
from ..serializers import TagSerializer
from .. import models, utils


class TagView(APIView):
    """
    [GET, POST]: /tag/
    {id: int, value: str}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Get tag list

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        return Response(
            tuple(TagSerializer(tag).data for tag in models.Tag.objects.all()),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Create Tag
        """
        serializer = TagSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": utils.serialize_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as err:
            response = Response(
                {"errors": {"value": (str(err.__cause__),)}},
                status=status.HTTP_409_CONFLICT,
            )

        return response


class TagDetailView(APIView):
    """
    [GET] /tag/<int:pk>/
    {id: int, value: str}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """Get tag detail

        Args:
            request (HttpRequest): Django HttpRequest
            pk (str): Tag primary key

        Returns:
            Response: DRF Response
        """
        try:
            tag = models.Tag.objects.get(id=pk)

        except models.Tag.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)

        else:
            response = Response(TagSerializer(tag).data, status=status.HTTP_200_OK)

        return response


@api_view(["GET"])
def tag_kinds(request):
    """returns choices for kinds of tags

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        Response: DRF Response
    """
    return Response(models.Tag.KIND, status=status.HTTP_200_OK)
