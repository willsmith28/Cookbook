<template>
  <md-autocomplete
    v-model="name"
    md-input-id="ingredient"
    md-input-name="ingredient"
    :md-options="ingredientNames"
    @md-selected="onSelect()"
  >
    <label>Ingredient</label>
    <template slot="md-autocomplete-empty" slot-scope="{ term }">
      <a @click="addIngredient(term)">Create {{ term }} ingredient!</a>
    </template>
    <span v-show="value" class="md-helper-text">
      selected Ingredient
      <ingredient-name-link :ingredient-id="value" />
    </span>
    <span v-show="showRequiredError" class="md-error">
      Ingredient is required
    </span>
  </md-autocomplete>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import IngredientNameLink from "@/components/IngredientNameLink";
export default {
  name: "IngredientAutocomplete",
  components: { IngredientNameLink },
  props: {
    value: { type: [Number, String], default: null },
    showRequiredError: { type: Boolean, default: false }
  },
  data: () => ({ name: null }),
  computed: {
    ingredientIdsByName() {
      return Object.assign(
        {},
        ...this.ingredients.map(item => ({ [item.name]: item.id }))
      );
    },
    ...mapGetters("recipe", ["ingredients", "ingredientNames", "getIngredient"])
  },
  created() {
    if (this.ingredients.length) {
      if (this.value) {
        const ingredient = this.getIngredient(this.value);
        this.name = ingredient ? ingredient.name : null;
      }
    } else {
      this.fetchAllIngredients().then(() => {
        if (this.value) {
          const ingredient = this.getIngredient(this.value);
          this.name = ingredient ? ingredient.name : null;
        }
      });
    }
  },
  methods: {
    onSelect() {
      this.$emit("input", this.ingredientIdsByName[this.name]);
    },
    async addIngredient(name) {
      try {
        this.name = name;
        await this.createIngredient({ recipeId: null, name });
        this.onSelect();
      } catch (error) {
        //TODO emit error?
      }
    },
    ...mapActions("recipe", ["createIngredient", "fetchAllIngredients"])
  }
};
</script>
