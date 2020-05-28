<template>
  <md-card class="recipe-overview-card">
    <md-card-header>
      <div class="md-title">
        {{ recipe.name }}
      </div>

      <div class="md-subhead">
        {{ formattedIngredientCount }} - {{ formattedStepCount }} -
        {{ recipe.cook_time }} - serves {{ recipe.servings }}
      </div>
    </md-card-header>

    <md-card-content>
      <p>
        {{ recipe.description }}
      </p>

      <div v-if="!!recipe.tags.length">
        <tag-chips :tag-ids="recipe.tags" />
      </div>
    </md-card-content>

    <md-card-actions>
      <md-button
        v-if="onDetailPage"
        :to="{ name: 'recipe-edit', params: { id: recipeId } }"
      >
        Edit
      </md-button>
      <md-button
        v-else
        :to="{ name: 'recipe-detail', params: { id: recipeId } }"
      >
        See Details
      </md-button>
    </md-card-actions>
  </md-card>
</template>

<script>
import TagChips from "@/components/TagChips";
import { mapGetters } from "vuex";
export default {
  name: "RecipeOverviewCard",
  components: { TagChips },
  props: {
    recipeId: {
      type: [Number, String],
      required: true
    }
  },
  computed: {
    onDetailPage() {
      return this.$route.name === "recipe-detail";
    },
    recipe() {
      return this.getRecipe(this.recipeId);
    },
    formattedIngredientCount() {
      const ingredientCount = this.ingredientInRecipeCount(this.recipeId);
      return `${ingredientCount} ingredient${ingredientCount > 1 ? "s" : ""}`;
    },
    formattedStepCount() {
      const stepCount = this.stepInRecipeCount(this.recipeId);
      return `${stepCount} step${stepCount > 1 ? "s" : ""}`;
    },
    ...mapGetters("recipe", [
      "ingredientInRecipeCount",
      "stepInRecipeCount",
      "getRecipe"
    ])
  }
};
</script>
