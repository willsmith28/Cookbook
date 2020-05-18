<template>
  <div>
    <div class="md-layout">
      <md-card class="md-layout-item">
        <md-card-header>
          <div class="md-title">{{ recipe.name }}</div>
        </md-card-header>

        <md-card-content>
          <p>{{ recipe.description }}</p>
          <p>Cook Time: {{ recipe.cook_time }}</p>
          <p>Number of servings: {{ recipe.servings }}</p>
        </md-card-content>
      </md-card>

      <md-card v-if="steps.length > 0" class="md-layout-item">
        <md-card-header>
          <div class="md-title">Steps</div>
        </md-card-header>

        <md-card-actions>
          <md-card-expand-triggers>
            <md-button class="md-icon-button">
              <md-icon>keyboard_arrow_down</md-icon>
            </md-button>
          </md-card-expand-triggers>
        </md-card-actions>

        <md-card-expand-content>
          <md-card-content>
            <md-list>
              <md-list-item
                v-for="(instruction, stepIndex) of steps"
                :key="stepIndex"
              >
                <div class="md-list-item-text">
                  {{ stepIndex + 1 }} {{ instruction }}
                </div>
              </md-list-item>
            </md-list>
          </md-card-content>
        </md-card-expand-content>
      </md-card>

      <md-card v-if="ingredients.length > 0" class="md-layout-item">
        <md-card-header>
          <div class="md-title">Ingredients</div>
        </md-card-header>

        <md-card-actions>
          <md-card-expand-trigger>
            <md-button class="md-icon-button">
              <md-icon>keyboard_arrow_down</md-icon>
            </md-button>
          </md-card-expand-trigger>
        </md-card-actions>

        <md-card-expand-content>
          <md-card-content>
            <md-list>
              <md-list-item
                v-for="(ingredient, ingredientIndex) in ingredients"
                :key="ingredientIndex"
              >
                <div class="md-list-item-text">
                  {{ toFraction(ingredient.amount) }}
                  {{ ingredient.unit }}
                  <ingredient-name-link
                    :ingredient-id="ingredient.ingredient_id"
                  />
                  {{ ingredient.specifier }}
                </div>
              </md-list-item>
            </md-list>
          </md-card-content>
        </md-card-expand-content>
      </md-card>
    </div>
  </div>
</template>

<script>
import IngredientNameLink from "@/components/IngredientNameLink";
import Fraction from "fraction.js";
import { mapActions, mapGetters } from "vuex";
export default {
  components: { IngredientNameLink },
  props: {
    id: {
      type: [Number, String],
      required: true
    }
  },
  computed: {
    recipe() {
      return this.getRecipe(this.id);
    },
    ingredients() {
      return this.getIngredientsInRecipe(this.id);
    },
    steps() {
      return this.getSteps(this.id);
    },
    tags() {
      return this.recipe.tags.map(tagID => this.getTag(tagID));
    },
    ...mapGetters("recipe", [
      "getIngredient",
      "getRecipe",
      "getIngredientsInRecipe",
      "getSteps",
      "getTag"
    ])
  },
  created() {
    Promise.all([
      this.fetchIngredientsInRecipe(this.id),
      this.fetchStepsInRecipe(this.id)
    ]);
  },
  methods: {
    toFraction(number) {
      return new Fraction(number).toFraction(true);
    },
    ...mapActions("recipe", [
      "fetchIngredientsInRecipe",
      "fetchStepsInRecipe",
      "fetchRecipeDetail"
    ])
  }
};
</script>
