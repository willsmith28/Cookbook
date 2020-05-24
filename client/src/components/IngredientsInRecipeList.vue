<template>
  <div>
    <ul>
      <li
        v-for="(ingredient, ingredientIndex) in ingredients"
        :key="ingredientIndex"
      >
        <span>
          {{ ingredient.amount }}
          {{ ingredient.unit }}
          <ingredient-name-link :ingredient-id="ingredient.ingredientId" />
          {{ ingredient.specifier }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import Fraction from "fraction.js";
import IngredientNameLink from "@/components/IngredientNameLink";
import { mapGetters } from "vuex";
export default {
  name: "IngredientsInRecipeList",
  components: { IngredientNameLink },
  props: {
    recipeId: { type: [String, Number], required: true }
  },
  computed: {
    ingredients() {
      if (this.recipeId) {
        const ingredients = this.getIngredientsInRecipe(this.recipeId).map(
          ingredient => ({
            ...ingredient,
            amount: this.toFraction(ingredient.amount)
          })
        );
        return ingredients;
      } else {
        return [];
      }
    },
    ...mapGetters("recipe", ["getIngredientsInRecipe"])
  },
  methods: {
    toFraction(number) {
      return new Fraction(number).toFraction(true);
    }
  }
};
</script>

<style scoped>
ul {
  display: inline-block;
  text-align: left;
}
div {
  text-align: center;
}
</style>
