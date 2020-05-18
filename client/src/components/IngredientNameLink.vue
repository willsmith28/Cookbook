<template>
  <span>
    <span v-if="!!ingredient.recipe_id">
      <router-link
        :to="{
          name: 'recipe-detail',
          props: { id: ingredient.recipe_id }
        }"
      >
        {{ getRecipeName(ingredient.recipe_id) }}
      </router-link>
    </span>
    <span v-else>
      {{ ingredient.name }}
    </span>
  </span>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "IngredientNameLink",
  props: {
    ingredientID: {
      type: [String, Number],
      required: true
    }
  },
  computed: {
    ingredient() {
      return this.getIngredient(this.ingredientID);
    },
    ...mapGetters("recipe", ["getRecipeName", "getIngredient"])
  }
};
</script>
