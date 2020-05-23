"""RecipeManager urls
"""
from django.urls import path
from . import views

urlpatterns = [
    path("ingredients/", views.IngredientView.as_view(), name="ingredient"),
    path("ingredients/units/", views.ingredient_units, name="ingredient-units"),
    path(
        "ingredients/<int:pk>/",
        views.IngredientDetailView.as_view(),
        name="ingredient-detail",
    ),
    path("tags/", views.TagView.as_view(), name="tag"),
    path("tags/kind/", views.tag_kinds, name="tag_kind"),
    path("tags/<int:pk>/", views.TagDetailView.as_view(), name="tag-detail"),
    path("recipes/", views.RecipeView.as_view(), name="recipe"),
    path("recipes/<int:pk>/", views.RecipeDetailView.as_view(), name="recipe-detail"),
    path(
        "recipes/<int:recipe_pk>/ingredients/",
        views.RecipeIngredient.as_view(),
        name="recipe-ingredients",
    ),
    path(
        "recipes/<int:recipe_pk>/ingredients/<int:ingredient_pk>/",
        views.RecipeIngredientDetail.as_view(),
        name="recipe-ingredient-detail",
    ),
    path(
        "recipes/<int:recipe_pk>/steps/",
        views.RecipeStep.as_view(),
        name="recipe-steps",
    ),
    path(
        "recipes/<int:recipe_pk>/steps/<int:order>/",
        views.RecipeStepDetail.as_view(),
        name="recipe-step-detail",
    ),
    path(
        "recipes/<int:recipe_pk>/tags/", views.RecipeTag.as_view(), name="recipe-tags"
    ),
    path(
        "recipes/<int:recipe_pk>/tags/<int:tag_pk>/",
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
