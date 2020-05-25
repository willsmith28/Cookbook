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
      <span>
        <span>No ingredient matching "{{ term }}" could be found.</span>
        <md-button @click="addIngredient(term)">
          Create it!
        </md-button>
      </span>
    </template>
    <div v-show="value" class="md-helper-text">
      selected Ingredient {{ name }}
    </div>
  </md-autocomplete>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
export default {
  name: "IngredientAutocomplete",
  props: {
    value: { type: [Number, String], required: true, default: null }
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
    if (this.value) {
      const ingredient = this.getIngredient(this.ingredientId);
      this.name = ingredient ? ingredient.name : null;
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
    ...mapActions("recipe", ["createIngredient"])
  }
};
</script>
