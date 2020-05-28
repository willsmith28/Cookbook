<template>
  <div v-if="!!recipe" class="md-layout md-alignment-top-center">
    <recipe-overview-card :recipe-id="id" class="md-layout-item md-size-90" />

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
            <ingredients-in-recipe-list :recipe-id="id" />
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
        <ingredients-in-recipe-list :recipe-id="id" />
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
            <steps-list :recipe-id="id" />
          </md-card-content>
        </md-card-expand-content>
      </md-card-expand>

      <md-card-content v-else>
        <steps-list :recipe-id="id" />
      </md-card-content>
    </md-card>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import RecipeOverviewCard from "@/components/RecipeOverviewCard";
import IngredientsInRecipeList from "@/components/IngredientsInRecipeList";
import StepsList from "@/components/StepsList.vue";
export default {
  components: { IngredientsInRecipeList, StepsList, RecipeOverviewCard },
  props: {
    id: {
      type: [Number, String],
      required: true
    }
  },
  data: () => ({
    expandGreaterThan: 11
  }),
  computed: {
    recipe() {
      return this.getRecipe(this.id);
    },
    tags() {
      return this.recipe.tags.map(tagID => this.getTag(tagID));
    },
    numberStepsInRecipe() {
      return this.stepInRecipeCount(this.id);
    },
    numberIngredientsInRecipe() {
      return this.ingredientInRecipeCount(this.id);
    },
    pluralizeFormatIngredient() {
      return `Ingredient${this.numberIngredientsInRecipe === 1 ? "" : "s"}`;
    },
    pluralizeFormatStep() {
      return `Step${this.numberStepsInRecipe === 1 ? "" : "s"}`;
    },
    ...mapGetters("recipe", [
      "getRecipe",
      "ingredients",
      "tags",
      "ingredientInRecipeCount",
      "stepInRecipeCount",
      "getTag"
    ])
  },
  created() {
    const requests = [];
    if (!this.ingredients.length) {
      requests.push(this.fetchAllIngredients());
    }
    if (!this.tags.length) {
      requests.push(this.fetchAllTags());
    }
    if (this.id) {
      const recipe = this.getRecipe(this.id);
      console.log(recipe);
      if (!recipe) {
        requests.push(this.fetchRecipeDetail());
      }

      if (!requests.length) {
        Promise.all(requests);
      }
    } else {
      // router.push(404)
    }
  },
  methods: {
    ...mapActions("recipe", [
      "fetchRecipeDetail",
      "fetchTagDetail",
      "fetchAllIngredients",
      "fetchAllTags"
    ])
  }
};
</script>

<style scoped>
.md-card {
  margin: 4px;
}
</style>
