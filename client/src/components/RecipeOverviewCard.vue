<template>
  <router-link :to="{ name: 'recipe-detail', params: { id: recipe.id } }">
    <md-card md-with-hover>
      <md-ripple>
        <md-card-header>
          <div class="md-title">{{ recipe.name }}</div>
          <div class="md-subhead">
            {{ formattedIngredientCount }} - {{ formattedStepCount }} -
            {{ recipe.cook_time }} - serves {{ recipe.servings }}
          </div>
        </md-card-header>

        <md-card-content>
          <p>
            {{ recipe.description }}
          </p>
        </md-card-content>
      </md-ripple>
    </md-card>
  </router-link>
</template>

<script>
export default {
  props: {
    recipe: {
      type: Object,
      default: () => ({
        id: null,
        name: "",
        description: "",
        servings: null,
        cook_time: "",
        ingredients: [],
        steps: [],
        tags: []
      })
    }
  },
  computed: {
    formattedIngredientCount() {
      const ingredientCount = this.recipe.ingredients.length;
      return `${ingredientCount} ingredient${ingredientCount > 1 ? "s" : ""}`;
    },
    formattedStepCount() {
      const stepCount = this.recipe.steps.length;
      return `${stepCount} step${stepCount > 1 ? "s" : ""}`;
    }
  }
};
</script>
