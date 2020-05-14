"""RecipeManager urls
"""
from django.urls import path
from . import views

urlpatterns = [
    path("ingredient/", views.IngredientView.as_view(), name="ingredient"),
    path("ingredient/units/", views.ingredient_units, name="ingredient-units"),
    path(
        "ingredient/<int:pk>/",
        views.IngredientDetailView.as_view(),
        name="ingredient-detail",
    ),
    path("tag/", views.TagView.as_view(), name="tag"),
    path("tag/kind/", views.tag_kinds, name="tag_kind"),
    path("tag/<int:pk>/", views.TagDetailView.as_view(), name="tag-detail"),
    path("recipe/", views.RecipeView.as_view(), name="recipe"),
    path("recipe/<int:pk>/", views.RecipeDetailView.as_view(), name="recipe-detail"),
    path(
        "recipe/<int:recipe_pk>/ingredients/",
        views.RecipeIngredient.as_view(),
        name="recipe-ingredients",
    ),
    path(
        "recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/",
        views.RecipeIngredientDetail.as_view(),
        name="recipe-ingredient-detail",
    ),
    path(
        "recipe/<int:recipe_pk>/steps/", views.RecipeStep.as_view(), name="recipe-steps"
    ),
    path(
        "recipe/<int:recipe_pk>/steps/<int:step_pk>/",
        views.RecipeStepDetail.as_view(),
        name="recipe-step-detail",
    ),
    path("recipe/<int:recipe_pk>/tags/", views.RecipeTag.as_view(), name="recipe-tags"),
    path(
        "recipe/<int:recipe_pk>/tags/<int:tag_pk>/",
        views.RecipeTagDelete.as_view(),
        name="recipe-tags-delete",
    ),
    path("meal-plan/", views.MealPlanView.as_view(), name="meal-plan"),
    path(
        "meal-plan/<int:pk>/",
        views.MealPlanDetailView.as_view(),
        name="meal-plan-detail",
    ),
]
