<template>
  <div v-if="!!recipe" class="md-layout md-alignment-top-center">
    <recipe-overview-card
      :recipe-id="recipeId"
      class="md-layout-item md-size-90"
    />

    <md-card
      v-if="!!numberIngredientsInRecipe"
      class="md-layout-item md-xsmall-size-90 md-size-45"
    >
      <md-card-header>
        <div class="md-title">
          {{ numberIngredientsInRecipe }} {{ pluralizeFormatIngredient }}
        </div>
      </md-card-header>

      <md-card-expand v-if="numberIngredientsInRecipe > expandGreaterThan">
        <md-card-expand-content>
          <md-card-content>
            <ingredients-in-recipe-list :recipe-id="recipeId" />
          </md-card-content>
        </md-card-expand-content>
        <md-card-actions>
          <md-card-expand-trigger>
            <md-button class="md-icon-button">
              <md-icon>keyboard_arrow_down</md-icon>
            </md-button>
          </md-card-expand-trigger>
        </md-card-actions>
      </md-card-expand>
      <md-card-content v-else>
        <ingredients-in-recipe-list :recipe-id="recipeId" />
      </md-card-content>
    </md-card>

    <md-card
      v-if="!!numberStepsInRecipe"
      class="md-layout-item md-xsmall-size-90 md-size-45"
    >
      <md-card-header>
        <div class="md-title">
          {{ numberStepsInRecipe }} {{ pluralizeFormatStep }}
        </div>
      </md-card-header>

      <md-card-expand v-if="numberStepsInRecipe > expandGreaterThan">
        <md-card-actions>
          <md-card-expand-trigger>
            <md-button class="md-icon-button">
              <md-icon>keyboard_arrow_down</md-icon>
              <md-tooltip md-direction="left" md-delay="300">
                See detail
              </md-tooltip>
            </md-button>
          </md-card-expand-trigger>
        </md-card-actions>

        <md-card-expand-content>
          <md-card-content>
            <steps-list :recipe-id="recipeId" />
          </md-card-content>
        </md-card-expand-content>
      </md-card-expand>

      <md-card-content v-else>
        <steps-list :recipe-id="recipeId" />
      </md-card-content>
    </md-card>
  </div>
</template>

<script>
import RecipeOverviewCard from "@/components/RecipeOverviewCard";
import IngredientsInRecipeList from "@/components/IngredientsInRecipeList";
import StepsList from "@/components/StepsList.vue";
import { mapActions, mapGetters } from "vuex";
export default {
  components: { IngredientsInRecipeList, StepsList, RecipeOverviewCard },
  props: {
    recipeId: {
      type: [Number, String],
      required: true
    }
  },
  data: () => ({
    expandGreaterThan: 11
  }),
  computed: {
    recipe() {
      return this.getRecipe(this.recipeId);
    },
    tags() {
      return this.recipe.tags.map(tagID => this.getTag(tagID));
    },
    numberStepsInRecipe() {
      return this.stepInRecipeCount(this.recipeId);
    },
    numberIngredientsInRecipe() {
      return this.ingredientInRecipeCount(this.recipeId);
    },
    pluralizeFormatIngredient() {
      return `Ingredient${this.numberIngredientsInRecipe === 1 ? "" : "s"}`;
    },
    pluralizeFormatStep() {
      return `Step${this.numberStepsInRecipe === 1 ? "" : "s"}`;
    },
    ...mapGetters("recipe", [
      "getRecipe",
      "ingredientInRecipeCount",
      "stepInRecipeCount",
      "getTag"
    ])
  },

  methods: {
    ...mapActions("recipe", ["fetchRecipeDetail", "fetchTagDetail"])
  }
};
</script>

<style scoped>
.md-card {
  margin: 4px;
}
</style>
