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
      required: true
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
