"""Recipe Manager Views
"""
from django.db import transaction, IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from . import models, utils, constants

# pylint: disable=no-self-use


class IngredientView(APIView):
    """
    [GET, POST]: /ingredient/
    {id: int, name: str, recipe_id: (int, None)}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Get list of all ingredients

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        return Response(
            tuple(
                ingredient.to_json() for ingredient in models.Ingredient.objects.all()
            ),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create new Ingredient

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        ingredient = request.data
        if errors := utils.validate_required_fields(
            ingredient, constants.REQUIRED_INGREDIENT_FIELDS
        ):
            return Response(
                {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST,
            )

        ingredient, created = models.Ingredient.objects.get_or_create(
            name=ingredient["name"], defaults={"recipe_id": ingredient["recipe_id"]}
        )

        return Response(
            ingredient.to_json(),
            status=status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT,
        )


class IngredientDetailView(APIView):
    """
    [GET]: /ingredient/<int:pk>/
    {id: int, name: str, recipe_id: (int, None)}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """Get ingredient

        Args:
            request (HttpRequest): Django HttpRequest
            pk (str): ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            ingredient = models.Ingredient.objects.get(id=pk)

        except models.Ingredient.DoesNotExist:
            response = Response(
                {"message": "No ingredient found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(ingredient.to_json(), status=status.HTTP_200_OK,)

        return response


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

        try:
            tag, created = models.Tag.objects.get_or_create(value=request_tag["value"])

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
        """[summary]

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


class RecipeView(APIView):
    """
    [GET, POST]: /recipe/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        tags: [int,]
        # POST only
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': (int, str)
            }
        ],
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                parent_recipe_id: int
                ingredient_id: int
            }
        ],
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Returns a list of all Recipes

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        return Response(
            tuple(
                recipe.to_json(with_tags=True)
                for recipe in models.Recipe.objects.prefetch_related("tags").all()
            ),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a new Recipe

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        # validate request data
        recipe = request.data
        user = request.user

        if errors := utils.validate_recipe(recipe):
            return Response(
                {"message": ". ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                recipe = utils.create_recipe(recipe, user.id)

        except models.Ingredient.DoesNotExist:
            response = Response(
                {"message": "A provided ingredient ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                recipe.to_json(with_tags=True), status=status.HTTP_201_CREATED,
            )

        return response


class RecipeDetailView(APIView):
    """
    [GET, PUT]: /recipe/<int:pk>/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        tags: [int,]
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': (int, str)
            }
        ],
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                parent_recipe_id: int
                ingredient_id: int
            }
        ],
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """Get Recipe detail

        Args:
            request (HttpRequest): Django HttpRequest
            pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags", "steps").get(id=pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "No Recipe was found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(
                {
                    **recipe.to_json(with_tags=True),
                    "steps": tuple(step.to_json() for step in recipe.steps.all()),
                    "ingredients": tuple(
                        ingredient.to_json()
                        for ingredient in models.IngredientInRecipe.objects.filter(
                            parent_recipe_id=pk
                        )
                    ),
                },
                status=status.HTTP_200_OK,
            )

        return response

    def put(self, request, pk):
        """Edit an existing recipe

        Args:
            request (HttpRequest): Django HttpRequest
            pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags", "steps").get(id=pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "No Recipe was found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        request_recipe = utils.extract_required_fields(
            request.data, constants.REQUIRED_RECIPE_FIELDS
        )
        edit = False

        for field, value in request_recipe.items():
            if value is not None and value != getattr(recipe, field):
                setattr(recipe, field, value)
                edit = True

        try:
            if edit:
                recipe.save()

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                recipe.to_json(with_tags=True), status=status.HTTP_200_OK,
            )

        return response


class RecipeIngredient(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/ingredients/
    {
        amount: decimal,
        unit: str,
        specifier: str,
        ingredient_id: (int, str)
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get a list of ingredients in a recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        else:
            response = Response(
                tuple(
                    ingredient.to_json()
                    for ingredient in models.IngredientInRecipe.objects.filter(
                        parent_recipe_id=recipe.id
                    )
                ),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Add ingredient to recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        recipe_ingredient = request.data

        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)
            ingredient = models.Ingredient.objects.get(
                id=recipe_ingredient["ingredient_id"]
            )
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except models.Ingredient.DoesNotExist:
            return Response(
                {"message": "Invalid ingredient_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # validate request data
        if errors := utils.validate_required_fields(
            recipe_ingredient, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        ):
            return Response(
                {"message": ". ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        recipe_ingredient = utils.extract_required_fields(
            recipe_ingredient, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        )

        try:
            recipe_ingredient = models.IngredientInRecipe.objects.create(
                parent_recipe_id=recipe.id, ingredient=ingredient, **recipe_ingredient,
            )

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                recipe_ingredient.to_json(), status=status.HTTP_201_CREATED,
            )

        return response


class RecipeIngredientDetail(APIView):
    """
    [GET, PUT, DELETE]
    /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
    {
        amount: decimal, str,
        unit: str,
        specifier: str,
        ingredient_id: int
        GET only
        name: str
        recipe_id: int
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk, ingredient_pk):
        """
        Get Ingredient in recipe detail

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            response = Response(recipe_ingredient.to_json(), status=status.HTTP_200_OK,)

        return response

    def put(self, request, recipe_pk, ingredient_pk):
        """
        Edit Ingredient in recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe_ingredient = models.IngredientInRecipe.objects.select_related(
                "ingredient", "parent_recipe"
            ).get(ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk)

        except models.IngredientInRecipe.DoesNotExist:
            return Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe_ingredient.parent_recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        request_recipe_ingredient = utils.extract_required_fields(
            request.data, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        )

        edited = False
        for key, value in request_recipe_ingredient.items():
            if value is not None and value != getattr(recipe_ingredient, key):
                setattr(recipe_ingredient, key, value)
                edited = True

        try:
            if edited:
                recipe_ingredient.save()

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_409_CONFLICT
            )
        else:
            response = Response(recipe_ingredient.to_json(), status=status.HTTP_200_OK,)

        return response

    def delete(self, request, recipe_pk, ingredient_pk):
        """
        Remove Ingredient from recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            models.Recipe.objects.values("id").get(id=recipe_pk)
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk
            )
        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            recipe_ingredient.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        return response


class RecipeStep(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/steps/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
    Args:
        APIView ([type]): [description]
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get list of steps in the recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("steps").get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            response = Response(
                tuple(step.to_json() for step in recipe.steps.all()),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Create new step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        step = request.data
        current_step_count = recipe.steps.count()

        try:
            step = recipe.steps.create(
                instruction=step["instruction"], order=current_step_count + 1
            )

        except KeyError:
            response = Response(
                {"message": "instruction is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_201_CREATED)

        return response


class RecipeStepDetail(APIView):
    """
    [GET, PUT, DELETE] /recipe/<int:recipe_pk>/steps/<int:step_pk>/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk, step_pk):
        """get step detail

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            models.Recipe.objects.values("id").get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_200_OK)

        return response

    def put(self, request, recipe_pk, step_pk):
        """edit a step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.values("author_id").get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe["author_id"]:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            if (instruction := request.data["instruction"]) != step.instruction:
                step.instruction = instruction
                step.save()

        except KeyError:
            response = Response(
                {"message": "instruction is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_200_OK)

        return response

    def delete(self, request, recipe_pk, step_pk):
        """Delete Step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if recipe.steps.count() == step.order:
            step.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        else:
            response = Response(
                {"message": "Steps must be deleted in decresing order"},
                status=status.HTTP_409_CONFLICT,
            )

        return response


class RecipeTag(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/tags/
    {
        id: int,
        value: str
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get all tags on this recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF response
        """

        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(
                tuple(tag.to_json() for tag in recipe.tags.all()),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Add new tag to this recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)

            if "value" in request.data:
                tag, _ = models.Tag.objects.get_or_create(value=request.data["value"])
            else:
                tag = models.Tag.objects.get(id=request.data["id"])

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except KeyError:
            return Response(
                {"message": "id or name field is a required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        recipe.tags.add(tag)

        return Response(tag.to_json(), status=status.HTTP_201_CREATED)


class RecipeTagDelete(APIView):
    """
    [DELETE] /recipe/<int:recipe_pk>/tags/<tag_pk>/
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def delete(self, request, recipe_pk, tag_pk):
        """Remove a tag from a recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            tag_pk (int): Tag primary key

        Returns:
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)
            tag = models.Tag.objects.get(id=tag_pk)
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except models.Tag.DoesNotExist:
            return Response(
                {"message": "Tag with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        recipe.tags.remove(tag)

        return Response(status=status.HTTP_204_NO_CONTENT)
