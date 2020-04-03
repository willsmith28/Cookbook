"""Common functionality like creating and validating models
"""
from typing import Iterable, Union, Tuple
from . import models, constants


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


def validate_recipe(recipe: dict) -> Tuple[str]:
    """check if a recipe is valid. includes ingredients step and tag validation
    {
        name: str
        description: str
        servings: int
        cook_time: str,
        ingredients: [{
            amount: decimal,
            unit: str,
            specifier: str,
            ingredient_id: (int, str)
        }, ...]
        steps: [{
            'instruction': str,
        }, ...]
        tags: [int, ...]
    }

    Args:
        recipe (dict): dict representation of a recipe

    Returns:
        Tuple[str]: list of errors
    """
    return (
        *validate_required_fields(recipe, constants.REQUIRED_RECIPE_FIELDS),
        *validate_recipe_steps(recipe.get("steps", ())),
        *validate_recipe_ingredients(recipe.get("ingredients", ())),
        *validate_tags(recipe.get("tags", ())),
    )


def validate_recipe_steps(steps: Iterable[dict]) -> Tuple[str]:
    """Validates provided steps.
    returns list of errors or empty list if no errors.
    steps should be as exampled below
    [
        {
            'order': int,
            'instruction': str,
        }
    ]

    Args:
        steps (Iterable[dict]): steps in recipe

    Returns:
        Tuple[str]: list of errors
    """
    errors = ()

    try:
        if any("instruction" not in step for step in steps):
            errors = ("instruction is a required field for step.",)

    except TypeError:
        errors = ("steps must be a list of steps",)

    return errors


def validate_recipe_ingredients(ingredients: Iterable[dict]) -> Tuple[str]:
    """validates provided ingredients
    returns list of errors or empty list if no errors.
    ingredients should be as exampled below
    [
        {
            amount: decimal,
            unit: str,
            specifier: str,
            ingredient_id: (int, str)
        }
    ]

    Args:
        ingredients (Iterable[dict]): ingredients in recipe

    Returns:
        Tuple[str]: list of errors
    """

    try:
        errors = {
            err_msg
            for ingredient in ingredients
            for err_msg in validate_required_fields(
                ingredient, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
            )
        }

    except TypeError:
        errors = (
            "ingredients must be a list of objects with "
            "ingredient_id, amount, unit, and specifier.",
        )

    return tuple(errors)


def validate_tags(tags: Iterable[Union[str, int]]) -> Tuple[str]:
    """validates provided tag IDs
    returns list of errors or empty list if no errors.
    ingredients should be as exampled below

    Args:
        tags (Iterable[Union[str, int]]): list of IDs

    Returns:
        Tuple[str]: list of errors
    """
    errors = ()
    try:
        if any(not isinstance(tag_id, (str, int)) for tag_id in tags):
            errors = ("tag ID must be either a string or an integer",)

    except TypeError:
        errors = ("tags must be a list of tag IDs",)

    return errors


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
