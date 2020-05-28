<template>
  <span v-if="ingredientId && ingredient">
    <span v-if="!!ingredient.recipeId">
      <router-link
        :to="{
          name: 'recipe-detail',
          props: { id: ingredient.recipeId }
        }"
      >
        {{ getRecipeName(ingredient.recipeId) }}
      </router-link>
    </span>
    <b v-else>
      {{ ingredient.name }}
    </b>
  </span>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "IngredientNameLink",
  props: {
    ingredientId: {
      type: [String, Number],
      default: null
    }
  },
  computed: {
    ingredient() {
      return this.getIngredient(this.ingredientId);
    },
    ...mapGetters("recipe", ["getRecipeName", "getIngredient"])
  }
};
</script>
