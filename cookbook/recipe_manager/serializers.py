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

    def validate_recipe_id(self, value):
        """
        Validate Recipe ID exists
        """
        try:
            if value is not None:
                models.Recipe.objects.get(id=value)

        except models.Recipe.DoesNotExist:
            raise serializers.ValidationError("Recipe with that ID does not exist")

        return value

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
    unit = serializers.ChoiceField(models.IngredientInRecipe.UNITS)
    specifier = serializers.CharField(max_length=256, allow_blank=True)
    ingredient_id = serializers.IntegerField()
    recipe_id = serializers.IntegerField(required=False)

    def validate_ingredient_id(self, value):
        """
        Validate Ingredient ID exists
        """
        try:
            models.Ingredient.objects.get(id=value)

        except models.Ingredient.DoesNotExist:
            raise serializers.ValidationError("Ingredient with that ID does not exist")

        return value

    def create(self, validated_data):
        return models.IngredientInRecipe.objects.create(**validated_data)

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
    order = serializers.IntegerField(min_value=1)
    recipe_id = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return models.Step.objects.create(**validated_data)

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

    def validate_recipe_id(self, value):
        """
        Validate Recipe ID exists
        """
        try:
            models.Recipe.objects.get(id=value)

        except models.Recipe.DoesNotExist:
            raise models.Recipe.DoesNotExist

        return value

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
