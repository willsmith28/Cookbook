"""Common functionality like creating and validating models
"""
from typing import Iterable, Union, Tuple
from . import models, constants, serializers


def user_owns_item(author_id: int, user_id: int, is_superuser: bool) -> bool:
    """checks if user owns thing they are trying to edit

    Args:
        author_id (int): author ID of item
        user_id (int): [description]
        is_superuser (bool): [description]

    Returns:
        bool: [description]
    """
    return user_id == author_id or is_superuser


def serialize_errors(errors: dict) -> dict:
    """Creates a copy of serializer errors dict with error messages cast to string

    Args:
        errors (dict): serializer errors dict

    Returns:
        dict: new dict with error messages cast to string
    """
    return {
        key: tuple(str(error) for error in errors) for key, errors in errors.items()
    }


def validate_required_fields(item: dict, required_fields: Iterable[str]) -> Tuple[str]:
    """Validate that all required fields are in the provided item

    Args:
        item (dict): item to validate
        required_fields (Iterable[str]): fields to check object for

    Returns:
        Tuple[str]: list of x is a required field messages
    """
    return tuple(
        f"{field} is a required field" for field in required_fields if field not in item
    )


def extract_required_fields(item: dict, required_fields: Iterable[str]) -> dict:
    """returns a new dictionary with only the required fields

    Args:
        item (dict): item to strip fields from
        required_fields (Iterable[str]): list of fields to be in new dictionary

    Returns:
        dict: dictionary containing the fields in required_fields.
        The fields is None if it was missing from item
    """
    return {field: item.get(field) for field in required_fields}


def validate_recipe(data):
    """[summary]

    Args:
        data ([type]): [description]
    """

    def add_errors_to_dict(errors, key, invalid_serializers):
        for index, serializer in invalid_serializers:
            errors[key][index] = serialize_errors(serializer.errors)

    def get_invalid_serializers_with_index(serializers_sequence):
        return tuple(
            (str(index), serializer)
            for index, serializer in enumerate(serializers_sequence)
            if not serializer.is_valid()
        )

    errors = {}

    if isinstance(ingredients := data.pop("ingredients", ()), (list, tuple)):
        ingredient_in_recipe_serializers = tuple(
            serializers.IngredientInRecipeSerializer(data=ingredient)
            for ingredient in ingredients
        )

    else:
        errors["ingredients"] = {
            "non_field_errors": [
                "ingredients must be an Array of RecipeInIngredient objects"
            ]
        }

    steps = data.pop("steps", ())
    if isinstance(steps, (list, tuple)):
        step_serializers = tuple(
            serializers.StepSerializer(
                data={"order": index, "instruction": instruction}
            )
            for index, instruction in enumerate(steps, 1)
        )

    else:
        errors["steps"] = {"non_field_errors": ["steps must be an Array of Strings"]}

    if isinstance(tags := data.pop("tags", ()), (list, tuple)):
        try:
            tag_ids = tuple(int(tag_id) for tag_id in tags)
        except ValueError:
            errors["tags"] = {"non_field_errors": ["tags must be an array of Tag IDs"]}

    else:
        errors["tags"] = {"non_field_errors": ["tags must be an Array of Tag IDs"]}

    recipe_serializer = serializers.RecipeSerializer(data=data)

    if not recipe_serializer.is_valid():
        errors.update(serialize_errors(recipe_serializer.errors))

    if any(field in errors for field in ("ingredients", "steps", "tags")):
        return errors, {"recipe": recipe_serializer}

    if invalid_serializers := get_invalid_serializers_with_index(
        ingredient_in_recipe_serializers
    ):
        errors["ingredients"] = {}
        add_errors_to_dict(errors, "ingredients", invalid_serializers)

    if invalid_serializers := get_invalid_serializers_with_index(step_serializers):
        errors["steps"] = {}
        add_errors_to_dict(errors, "steps", invalid_serializers)

    return (
        errors,
        {
            "recipe": recipe_serializer,
            "ingredients": ingredient_in_recipe_serializers,
            "steps": step_serializers,
            "tag_ids": tag_ids,
        },
    )


def create_recipe(recipe: dict, author_id: Union[int, str]) -> models.Recipe:
    """Create a new recipe with its relationships

    Args:
        recipe (dict): dict representation of recipe to make
        user_id (Union[int, str]): user id for author

    Returns:
        models.Recipe: newly created Recipe
    """
    ingredients_in_recipe = recipe.pop("ingredients", ())
    steps = recipe.pop("steps", ())
    tags = recipe.pop("tags", ())

    new_recipe = models.Recipe.objects.create(
        author_id=author_id,
        **extract_required_fields(recipe, constants.REQUIRED_RECIPE_FIELDS),
    )

    for ingredient_in_recipe in ingredients_in_recipe:
        ingredient = extract_required_fields(
            ingredient_in_recipe, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        )
        new_recipe.ingredients.add(
            models.Ingredient.objects.get(id=ingredient.pop("ingredient_id")),
            through_defaults=ingredient,
        )

    for index, step in enumerate(steps):
        new_recipe.steps.create(instruction=step["instruction"], order=index + 1)

    for tag_id in tags:
        try:
            tag = models.Tag.objects.get(id=tag_id)
            new_recipe.tags.add(tag)
        except models.Tag.DoesNotExist:
            pass

    return new_recipe
