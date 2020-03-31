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
    {id: int, name: str}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Get list of all ingredients

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        ingredients = tuple(
            ingredient.to_json() for ingredient in models.Ingredient.objects.all()
        )

        return Response(ingredients, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Ingredient

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        request_ingredient = request.data
        try:
            ingredient, created = models.Ingredient.objects.get_or_create(
                name=request_ingredient["name"]
            )
        except KeyError:
            return Response(
                {"message": "name is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ingredient.to_json(),
            status=(status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT),
        )


class IngredientDetailView(APIView):
    """
    [GET]: /ingredient/<int:pk>/
    {id: int, name: str}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """[summary]

        Args:
            request (HttpRequest): Django HttpRequest
            pk (str): ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            ingredient = models.Ingredient.objects.get(id=pk)
        except models.Ingredient.DoesNotExist:
            return Response(
                {"message": "No ingredient found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ingredient.to_json(), status=status.HTTP_200_OK,)


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
        tags = tuple(tag.to_json() for tag in models.Tag.objects.all())

        return Response(tags, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create Tag
        """
        request_tag = request.data

        try:
            tag, created = models.Tag.objects.get_or_create(value=request_tag["value"])
        except KeyError:
            return Response(
                {"message": "value is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            tag.to_json(),
            status=(status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT),
        )


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
            return Response(
                {"message": "Tag with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(tag.to_json(), status=status.HTTP_200_OK)


class RecipeView(APIView):
    """
    [GET, POST]: /recipe/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        tags: [{id: int, value: str}]
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
                name: str,
                recipe_id: (int, str, None)
                parent_recipe_id: (int, str)
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
        recipes = models.Recipe.objects.prefetch_related("tags").all()

        recipes = tuple(recipe.to_json(with_tags=True) for recipe in recipes)

        return Response(recipes, status=status.HTTP_200_OK,)

    def post(self, request):
        """Create a new Recipe

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        request_recipe = request.data
        user = request.user

        errors = (
            *utils.validate_recipe_ingredients(request_recipe.get("ingredients", ())),
            *utils.validate_recipe_steps(request_recipe.get("steps", ())),
            *utils.validate_tags(request_recipe.get("tags", ())),
        )

        if errors:
            return Response(
                {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                recipe = utils.create_recipe(
                    request_recipe, user.id, eager_load_relations=True,
                )
        except IntegrityError as err:
            return Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        serialized_recipe = utils.serialize_recipe_with_relationships(recipe)

        return Response(serialized_recipe, status=status.HTTP_201_CREATED)


class RecipeDetailView(APIView):
    """
    [GET, PUT]: /recipe/<int:pk>/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': (int, str)
            }
        ],
        # GET only
        tags: [{id: int, value: str}]
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                name: str,
                recipe_id: (int, str, None)
                parent_recipe_id: (int, str)
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
            return Response(
                {"message": "No Recipe was found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serialized_recipe = utils.serialize_recipe_with_relationships(recipe)

        return Response(serialized_recipe, status=status.HTTP_200_OK)

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

        if not request.user.is_superuser and request.user.id != recipe.author_id:
            return Response(
                {"message": "Cannot edit a recipe that is not yours"},
                status=status.HTTP_403_FORBIDDEN,
            )

        request_recipe = request.data

        edit = False
        response = None

        if (new_steps := request_recipe.pop("steps", None)) is not None:
            if errors := utils.validate_recipe_steps(new_steps):
                return Response(
                    {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                with transaction.atomic():
                    utils.update_steps(recipe, new_steps)

                edit = True

            except IntegrityError as err:
                response = Response(
                    {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST,
                )
            except KeyError:
                response = Response(
                    {"message": "Missing required field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if response is not None:
                return response

        recipe_fields = {"name", "description", "servings", "cook_time"}

        for field, value in request_recipe.items():
            if field in recipe_fields:
                if value != getattr(recipe, field):
                    setattr(recipe, field, value)
                    edit = True

        if edit:
            try:
                recipe.save()
            except IntegrityError as err:
                return Response(
                    {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
                )

        serialized_recipe = recipe.to_json(with_tags=True, with_steps=True)

        return Response(serialized_recipe, status=status.HTTP_200_OK)


class RecipeIngredient(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/ingredients/
    {
        amount: decimal,
        unit: str,
        specifier: str,
        name: str,
        recipe_id: (int, str, None)
        parent_recipe_id: (int, str)
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
            recipe = models.Recipe.objects.only("id").get(id=recipe_pk)
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        ingredients = models.IngredientInRecipe.objects.select_related(
            "ingredient"
        ).filter(parent_recipe_id=recipe.id)

        ingredients = tuple(
            ingredient.to_json(with_ingredient_info=True) for ingredient in ingredients
        )

        return Response(ingredients, status=status.HTTP_200_OK,)

    def post(self, request, recipe_pk):
        """Add ingredient to recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.only("id", "author_id").get(id=recipe_pk)
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_superuser and request.user.id != recipe.author_id:
            return Response(
                {"message": "Cannot edit a recipe that is not yours"},
                status=status.HTTP_403_FORBIDDEN,
            )

        recipe_ingredient = request.data

        errors = []
        for field in constants.REQUIRED_RECIPE_INGREDIENT_FIELDS:
            if field not in recipe_ingredient:
                errors.append(f"{field} is a required field")

        if errors:
            return Response(
                {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        ingredient, _ = models.Ingredient.objects.get_or_create(
            name=recipe_ingredient.pop("name"),
            recipe_id=recipe_ingredient.pop("recipe_id"),
        )

        try:
            recipe_ingredient = models.IngredientInRecipe.objects.create(
                parent_recipe_id=recipe.id, ingredient=ingredient, **recipe_ingredient
            )
        except IntegrityError as err:
            return Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            recipe_ingredient.to_json(with_ingredient_info=True),
            status=status.HTTP_201_CREATED,
        )


class RecipeIngredientDetail(APIView):
    """
    [GET, PUT, DELETE]
    /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/  # noqa: E501
    {
        amount: decimal,
        unit: str,
        specifier: str,
        name: str,
        recipe_id: (int, str, None)
        parent_recipe_id: (int, str)
    }
    """

    def get(self, request, recipe_pk, ingredient_pk):
        """
        Get Ingredient in recipe detail
        """
        try:
            recipe_ingredient = models.IngredientInRecipe.objects.select_related(
                "ingredient"
            ).get(ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk)
        except models.IngredientInRecipe.DoesNotExist:
            return Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            recipe_ingredient.to_json(with_ingredient_info=True),
            status=status.HTTP_200_OK,
        )

    def put(self, request, recipe_pk, ingredient_pk):
        """
        Edit Ingredient in recipe
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
            return Response(
                {"message": "Cannot edit a recipe that is not yours"},
                status=status.HTTP_403_FORBIDDEN,
            )

        edited = False

        request_recipe_ingredient = request.data

        recipe_ingredient_fields = {"amount", "unit", "specifier"}
        for key, value in request_recipe_ingredient.items():
            if key in recipe_ingredient_fields:
                setattr(recipe_ingredient, key, value)
                edited = True

        if edited:
            try:
                recipe_ingredient.save()
            except IntegrityError as err:
                return Response(
                    {"message": str(err.__cause__)}, status=status.HTTP_409_CONFLICT
                )

        return Response(
            recipe_ingredient.to_json(with_ingredient_info=True),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, recipe_pk, ingredient_pk):
        """
        Remove Ingredient from recipe
        """
        try:
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk
            )
        except models.IngredientInRecipe.DoesNotExist:
            return Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe_ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeTag(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/tags/
    {
        id: int,
        value: str
    }
    """

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
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        tags = tuple(tag.to_json() for tag in recipe.tags.all())

        return Response(tags, status=status.HTTP_200_OK)

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
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.is_superuser and request.user.id != recipe.author_id:
            return Response(
                {"message": "Cannot edit a recipe that is not yours"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            tag = models.Tag.objects.get_or_create(value=request.data["value"])
        except KeyError:
            return Response(
                {"message": '"value" is a required field'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe.tags.add(tag)

        return Response(tag.to_json(), status=status.HTTP_201_CREATED)


class RecipeTagDelete(APIView):
    """
    [DELETE] /recipe/<int:recipe_pk>/tags/<tag_pk>
    """

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
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            tag = models.Tag.objects.get(id=tag_pk)
        except models.Tag.DoesNotExist:
            return Response(
                {"message": "Tag with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe.tags.remove(tag)

        return Response(status=status.HTTP_204_NO_CONTENT)
