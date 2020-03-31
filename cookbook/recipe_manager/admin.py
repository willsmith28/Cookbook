"""Register models to django admin
"""
from django.contrib import admin
from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Register Ingredient to admin
    """


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Register Tag to admin
    """


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Register Recipe to admin
    """


@admin.register(models.IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Register Tag to admin
    """


@admin.register(models.Step)
class StepAdmin(admin.ModelAdmin):
    """Register Step to admin
    """
