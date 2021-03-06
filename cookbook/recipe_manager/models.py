"""Django Models for RecipeManager"""
from django.db import models
from django.core import validators
from django.conf import settings
from django.utils import timezone


class Ingredient(models.Model):
    """Ingredients can either be a stand-alone ingredient or a link to a
       recipe that should be used as an ingredient

    Attributes:
        name (str): Ingredient name
        recipe (Union[Recipe, None]): recipe to be used as an ingredient

    """

    name = models.CharField(max_length=256, unique=True)
    recipe = models.OneToOneField(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="used_as_ingredient",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Ingredient: {self.id} {self.name}>"


class Tag(models.Model):
    """A tag associated to a recipe e.g. 'Crock-Pot', 'Quick To Make', ...

    Attributes:
        value (str): name of the tag
        kind (str): type of tag
    """

    KIND = (
        ("Cuisine", "Cuisine"),
        ("Meal", "Meal"),
        ("Prep Method", "Prep Method"),
    )

    value = models.CharField(max_length=256, unique=True)
    kind = models.CharField(max_length=256, choices=KIND)

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"<Tag: {self.id} {self.value}>"


class Recipe(models.Model):
    """A Recipe

    Attributes:
        name (str): recipe name
        description (str): description of recipe
        servings (int): number of servings recipe makes
        cook_time (str): how long it will take e.g 45 minutes, 1 hour 20 minutes
        created_on (datetime): when recipe was created
        last_updated_on (datetime): when recipe was last updated
        ingredients (QuerySet[Ingredient]): ingredients in this recipe
        tags (QuerySet[Tag]): tags associated to this recipe
        author (User): recipe owner
        users_that_favorited (QuerySet[User]): Users that have added this recipe to their favorites

    """

    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    servings = models.IntegerField(
        validators=(
            validators.MinValueValidator(
                1, message="servings must be greater than zero"
            ),
        )
    )
    cook_time = models.CharField(max_length=128)
    created_on = models.DateTimeField(auto_now_add=timezone.now,)
    last_updated_on = models.DateTimeField(auto_now=timezone.now)

    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        through_fields=("recipe", "ingredient"),
        related_name="used_in_recipes",
    )
    tags = models.ManyToManyField(Tag, related_name="recipes",)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_recipes",
        null=True,
        blank=True,
    )
    users_that_favorited = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="saved_recipes"
    )

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Recipe: {self.id} {self.name}>"


class IngredientInRecipe(models.Model):
    """Through model for Recipe and Ingredient that contains amounts

    Attributes:
        recipe (Recipe): recipe this ingredient is for
        ingredient (Ingredient): ingredient in recipe
        amount (decimal): numeric value of amount to put in recipe
        unit (str): unit of amount
        specifier (str): optional specifier e.g. 'chopped'

    """

    UNITS = (
        (
            "Volume",
            (
                ("tsp", "teaspoon"),
                ("tbsp", "tablespoon"),
                ("fl oz", "fluid ounce"),
                ("c", "cup"),
                ("pt", "pint"),
                ("qt", "quart"),
                ("gal", "gallon"),
                ("ml", "milliliter"),
                ("l", "liter"),
            ),
        ),
        ("Mass", (("lb", "pound"), ("oz", "ounce"), ("g", "gram"),)),
        ("Length", (("in", "inch"), ("mm", "millimeter"), ("cm", "centimeter"))),
        ("Other", (("pieces", ""), ("n/a", ""))),
    )
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(max_length=16, choices=UNITS)
    specifier = models.CharField(max_length=256, blank=True)

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients_in_recipe"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    class Meta:
        """Enforce no duplicate ingredients in recipe"""

        unique_together = ("recipe_id", "ingredient_id")

    def __str__(self):
        return f"{self.amount} {self.unit} {self.specifier}"

    def __repr__(self):
        return (
            f"<IngredientInRecipe: {self.id} "
            f"ingredient_id: {self.ingredient_id} recipe_id: {self.recipe} "
            f"amount: {self.amount} unit: {self.unit}>"
        )


class Step(models.Model):
    """Instructions to make recipe

    Attributes:
        order (int): step order
        instruction (str): text block with instruction
        recipe (Recipe): recipe this step goes to

    """

    order = models.IntegerField(
        validators=(
            validators.MinValueValidator(1, message="Step order must be start at 1"),
        )
    )
    instruction = models.TextField()

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")

    class Meta:
        unique_together = ("order", "recipe_id")
        ordering = ("order",)

    def __str__(self):
        return f"{self.order}) {self.instruction}"

    def __repr__(self):
        return f"<Step: {self.id} recipe_id: {self.recipe_id} order: {self.order}>"


class MealPlan(models.Model):
    """Table for user to plan recipes to cook and keep track of leftovers.

    Args:
        recipe (Recipe): Recipe to cook
        planned_date (date): date to cook recipe on
        meal (str): indicates breakfast lunch or dinner. optional
        cooked: (bool): Recipe was cooked
        user: (User): User associated to this meal plan
    """

    MEALS = (
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
        ("Snack", "Snack"),
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.PROTECT, related_name="meal_plans"
    )
    planned_date = models.DateField()
    meal = models.CharField(max_length=16, choices=MEALS, null=True)
    cooked = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meal_plans",
    )
