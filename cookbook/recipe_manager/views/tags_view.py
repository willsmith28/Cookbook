"""
Views for /tag/ and /tag/<pk>/
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .. import models, utils, constants


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
            tuple(tag.to_json() for tag in models.Tag.objects.all()),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Create Tag
        """
        request_tag = request.data

        if errors := utils.validate_required_fields(
            request_tag, constants.REQUIRED_TAG_FIELDS
        ):
            return Response(
                {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tag, created = models.Tag.objects.get_or_create(
                value=request_tag["value"], defaults={"kind": request_tag["kind"]}
            )

        except KeyError:
            response = Response(
                {"message": "value is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(
                tag.to_json(),
                status=status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT,
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
            response = Response(
                {"message": "Tag with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(tag.to_json(), status=status.HTTP_200_OK)

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
