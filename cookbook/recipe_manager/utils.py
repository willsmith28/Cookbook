"""Common functionality like creating and validating models
"""
import operator
import itertools
from typing import Iterable, List, Sequence, Union
from . import models, constants


def _step_order_valid(steps: Iterable[dict]) -> bool:
    """Validates that the given steps have 'order' attributes that are sequence 1..n

    Args:
        steps (Iterable[dict]): a collection of steps

    Returns:
        bool: true if steps are valid
    """
    for index, step in enumerate(sorted(steps, key=operator.itemgetter("order"))):
        if step["order"] != index + 1:
            return False

    return True


def validate_recipe_steps(steps: Sequence[dict]) -> List[str]:
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
        steps (Sequence[dict]): steps in recipe

    Returns:
        List[str]: list of errors
    """
    errors = []

    try:
        if any(
            field not in step
            for step in steps
            for field in constants.REQUIRED_STEP_FIELDS
        ):
            errors.append("An included step is missing a field")

        if not steps:
            errors.append("Recipe must have at least one step.")
        elif not _step_order_valid(steps):
            errors.append('"steps" must be sequential.')
    except TypeError:
        errors.append('"steps" must be a list of steps')

    return errors


def validate_recipe_ingredients(ingredients: Sequence[dict]) -> List[str]:
    """validates provided ingredients
    returns list of errors or empty list if no errors.
    ingredients should be as exampled below
    [
        {
            amount: decimal,
            unit: str,
            specifier: str,
            name: str,
            recipe_id: (int, str, None)
        }
    ]

    Args:
        ingredients (Sequence[dict]): ingredients in recipe

    Returns:
        List[str]: list of errors
    """
    errors = []

    try:
        if any(
            field not in ingredient
            for ingredient in ingredients
            for field in constants.REQUIRED_RECIPE_INGREDIENT_FIELDS
        ):
            errors.append("An included recipe ingredient is missing a required field")

        if not ingredients:
            errors.append("Recipe must have at least one ingredient")
    except TypeError:
        errors.append('"ingredients" must be a list')

    return errors


def validate_tags(tags: Sequence[dict]) -> List[str]:
    """validates provided tags
    returns list of errors or empty list if no errors.
    ingredients should be as exampled below

    Args:
        tags (Sequence[dict]): list of tags

    Returns:
        List[str]: list of errors
    """
    required_field = "value"
    errors = []
    try:
        if any(required_field not in tag for tag in tags):
            errors.append("an Included tag is missing the its 'value' field")

    except TypeError:
        errors.append("tags must be a list")

    return errors


def serialize_recipe_with_relationships(recipe: models.Recipe) -> dict:
    """create a json serializable representation of a Recipe with its relationships

    Args:
        recipe (models.Recipe): [description]

    Returns:
        dict: [description]
    """
    ingredients_in_recipe = models.IngredientInRecipe.objects.select_related(
        "ingredient"
    ).filter(parent_recipe_id=recipe.id)

    serialized_recipe = recipe.to_json(with_tags=True, with_steps=True)

    serialized_recipe["ingredients"] = tuple(
        ingredient.to_json(with_ingredient_info=True)
        for ingredient in ingredients_in_recipe
    )

    return serialized_recipe


def create_recipe(
    recipe: dict, author_id: Union[int, str], eager_load_relations=False,
) -> models.Recipe:
    """Create a new recipe with its relationships

    Args:
        recipe (dict): dict representation of recipe to make
        user_id (Union[int, str]): user id for author
        eager_load_relations (bool, optional): eager load tags and steps. Defaults to False.

    Returns:
        models.Recipe: [description]
    """
    ingredients = recipe.pop("ingredients")
    steps = recipe.pop("steps")
    tags = recipe.pop("tags")

    new_recipe = models.Recipe.objects.create(author_id=author_id, **recipe)

    for recipe_ingredient in ingredients:
        ingredient, _ = models.Ingredient.objects.get_or_create(
            name=recipe_ingredient.pop("name"),
            defaults={"recipe_id": recipe_ingredient.pop("recipe_id", None)},
        )

        models.IngredientInRecipe.objects.create(
            parent_recipe=new_recipe, ingredient=ingredient, **recipe_ingredient
        )

    for step in steps:
        models.Step.objects.create(recipe=new_recipe, **step)

    for tag in tags:
        tag, _ = models.Tag.objects.get_or_create(value=tag["value"])
        new_recipe.tags.add(tag)

    new_recipe.save()

    if eager_load_relations:
        new_recipe = models.Recipe.objects.prefetch_related("steps", "tags").get(
            id=new_recipe.id
        )

    return new_recipe


def update_steps(recipe: models.Recipe, new_steps: Iterable[dict]):
    """makes Recipe steps match the provided new steps

    Args:
        recipe (models.Recipe): Recipe to have steps updated
        new_steps (Iterable[dict]): list of new steps
    """
    steps = itertools.zip_longest(
        recipe.steps.all(), sorted(new_steps, key=operator.itemgetter("order"))
    )
    for db_step, new_step in steps:
        if db_step is not None and new_step is not None:
            assert db_step.order == new_step["order"]
            if db_step.instruction != new_step["instruction"]:
                db_step.instruction = new_step["instruction"]
                db_step.save()

        elif db_step is None and new_step is not None:
            models.Step.objects.create(recipe=recipe, **new_step)

        elif db_step is not None and new_step is None:
            db_step.delete()
