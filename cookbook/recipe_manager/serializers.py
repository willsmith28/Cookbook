"""Serializers for models
"""
from rest_framework import serializers
from . import models


class IngredientSerializer(serializers.Serializer):
    """Serialize and validate Ingredient

    Args:
        serializers ([type]): [description]
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=256)
    recipe_id = serializers.IntegerField(allow_null=True)

    def create(self, validated_data):
        return models.Ingredient.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.recipe_id = validated_data.get("recipe_id", instance.recipe_id)
        instance.save()

        return instance


class TagSerializer(serializers.Serializer):
    """[summary]

    Args:
        serializers ([type]): [description]
    """

    id = serializers.IntegerField(read_only=True)
    value = serializers.CharField(max_length=256)
    kind = serializers.ChoiceField(models.Tag.KIND)

    def validate_kind(self, value):
        """[summary]

        Args:
            value ([type]): [description]
        """
        if value not in (kind for kind, _ in models.Tag.KIND):
            raise serializers.ValidationError("Invalid Tag Kind")

        return value

    def create(self, validated_data):
        return models.Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.value = validated_data.get("value", instance.value)
        instance.kind = validated_data.get("kind", instance.kind)
        instance.save()

        return instance


class IngredientInRecipeSerializer(serializers.Serializer):
    """[summary]

    Args:
        serializers ([type]): [description]
    """

    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    unit = serializers.CharField(max_length=16)
    specifier = serializers.CharField(max_length=256, allow_blank=True)
    ingredient_id = serializers.IntegerField()

    def validate_unit(self, value):
        """[summary]

        Args:
            value ([type]): [description]

        Raises:
            serializers.ValidationError: [description]

        Returns:
            [type]: [description]
        """
        if not any(
            value == unit_short
            for _, units in models.IngredientInRecipe.UNITS
            for unit_short, _ in units
        ):
            raise serializers.ValidationError("Invalid Unit")

        return value

    def create(self, validated_data):
        raise NotImplementedError(
            "Use Recipe Instance ingredients.add() to add Ingredients to Recipes"
        )

    def update(self, instance, validated_data):
        instance.amount = validated_data.get("amount", instance.amount)
        instance.unit = validated_data.get("unit", instance.unit)
        instance.specifier = validated_data.get("specifier", instance.specifier)

        instance.save()

        return instance


class StepSerializer(serializers.Serializer):
    """[summary]

    Args:
        serializers ([type]): [description]
    """

    id = serializers.IntegerField(read_only=True)
    instruction = serializers.CharField()
    order = serializers.IntegerField(min_value=1, read_only=True)

    def create(self, validated_data):
        raise NotImplementedError(
            "Use Recipe Instance steps.create() to add Steps to Recipe"
        )

    def update(self, instance, validated_data):
        instance.order = validated_data.get("order", instance.order)
        instance.instruction = validated_data.get("instruction", instance.instruction)
        instance.save()

        return instance


class RecipeSerializer(serializers.Serializer):
    """[summary]

    Args:
        serializers ([type]): [description]
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=256)
    description = serializers.CharField()
    servings = serializers.IntegerField(min_value=1)
    cook_time = serializers.CharField(max_length=128)
    created_on = serializers.DateTimeField(read_only=True)
    last_updated_on = serializers.DateTimeField(read_only=True)
    author_id = serializers.IntegerField(allow_null=True)

    def create(self, validated_data):
        return models.Recipe.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.servings = validated_data.get("servings", instance.servings)
        instance.cook_time = validated_data.get("cook_time", instance.cook_time)
        instance.save()

        return instance


class MealPlanSerializer(serializers.Serializer):
    """[summary]

    Args:
        serializers ([type]): [description]
    """

    id = serializers.IntegerField(read_only=True)
    recipe_id = serializers.IntegerField()
    planned_date = serializers.DateField()
    meal = serializers.CharField(max_length=16, allow_null=True)
    cooked = serializers.BooleanField()
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        return models.MealPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.recipe_id = validated_data.get("recipe_id", instance.recipe_id)
        instance.planned_date = validated_data.get(
            "planned_date", instance.planned_date
        )
        instance.meal = validated_data.get("meal", instance.meal)
        instance.cooked = validated_data.get("cooked", instance.cooked)
        instance.user_id = validated_data.get("user_id", instance.user_id)
        instance.save()

        return instance
