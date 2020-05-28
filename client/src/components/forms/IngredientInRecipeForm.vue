<template>
  <div>
    <form novalidate @submit.prevent="validateForm()">
      <div class="md-layout md-gutter md-alignment-top-center">
        <md-card
          v-for="($ingredient, ingredientIndex) of $v.ingredientsInRecipe.$each
            .$iter"
          :key="ingredientIndex"
          class="md-layout-item md-size-100"
        >
          <md-card-content class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-small-size-100 md-size-25">
              <md-field :class="getValidationClass('amount', $ingredient)">
                <label for="amount">Amount</label>
                <md-input
                  id="amount"
                  v-model.number="$ingredient.amount.$model"
                  name="amount"
                  type="number"
                />
                <span v-if="!$ingredient.amount.required" class="md-error">
                  Amount is required
                </span>
                <span v-else-if="!$ingredient.amount.positive" class="md-error">
                  Amount must be positive
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100 md-size-25">
              <md-field :class="getValidationClass('unit', $ingredient)">
                <label for="unit">Unit</label>
                <ingredient-unit-select v-model="$ingredient.unit.$model" />
                <span v-if="!$ingredient.unit.required" class="md-error">
                  Unit is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100 md-size-25">
              <ingredient-autocomplete
                v-model="$ingredient.ingredientId.$model"
                :class="getValidationClass('ingredientId', $ingredient)"
                :show-required-error="!$ingredient.ingredientId.required"
              />
            </div>

            <div class="md-layout-item md-small-size-100 md-size-25">
              <md-field :class="getValidationClass('specifier', $ingredient)">
                <label for="specifier">Specifier</label>
                <md-input
                  id="specifier"
                  v-model.trim="$ingredient.specifier.$model"
                  name="specifier"
                />
              </md-field>
            </div>
          </md-card-content>

          <md-card-actions>
            <md-button
              class="md-secondary"
              @click="removeIngredientFromForm(ingredientIndex)"
            >
              Remove this ingredient
            </md-button>
          </md-card-actions>
        </md-card>
      </div>
      <div class="md-layout">
        <div class="md-layout-item">
          <md-button class="md-secondary" @click="addIngredientToForm()">
            Add New Ingredient
          </md-button>
        </div>
        <div class="md-layout-item">
          <md-button class="md-raised md-primary" type="submit">
            Save Ingredients
          </md-button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import uniqueFieldInList from "@/validations/uniqueFieldInList";
import getValidationClass from "@/validations/getValidationClass";
import IngredientUnitSelect from "@/components/forms/inputs/IngredientUnitSelect";
import IngredientAutocomplete from "@/components/forms/inputs/IngredientAutocomplete";
export default {
  name: "IngredientInRecipeForm",
  components: { IngredientUnitSelect, IngredientAutocomplete },
  mixins: [validationMixin],
  props: {
    recipeId: { type: [Number, String], required: true }
  },
  data: () => ({
    ingredientsInRecipe: [
      {
        amount: null,
        unit: null,
        ingredientId: null,
        specifier: ""
      }
    ]
  }),
  validations: {
    ingredientsInRecipe: {
      required,
      uniqueFieldInList: uniqueFieldInList("ingredientId"),
      minLength: minLength(1),
      $each: {
        amount: { required, positive: value => value > 0 },
        unit: { required },
        ingredientId: { required },
        specifier: {}
      }
    }
  },
  computed: {
    ...mapGetters("recipe", [
      "getIngredientsInRecipe",
      "ingredients",
      "ingredientUnits"
    ])
  },
  created() {
    const ingredientsInRecipe = this.getIngredientsInRecipe(this.recipeId);
    console.log(ingredientsInRecipe);
    if (ingredientsInRecipe.length) {
      this.ingredientsInRecipe = ingredientsInRecipe;
    }
  },
  methods: {
    getValidationClass(fieldName, $ingredientInRecipe) {
      return getValidationClass(fieldName, $ingredientInRecipe);
    },
    addIngredientToForm() {
      this.ingredientsInRecipe.push({
        amount: null,
        unit: null,
        specifier: "",
        ingredientId: null
      });
    },
    removeIngredientFromForm(index) {
      this.ingredientsInRecipe.splice(index, 1);
    },
    validateForm() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.submitForm();
      }
    },
    async submitForm() {
      const requests = [];
      const StateIngredientIds = new Set(
        this.getIngredientsInRecipe(this.recipeId).map(
          item => item.ingredientId
        )
      );
      const formIngredientIds = new Set();
      for (const ingredient of this.ingredientsInRecipe) {
        formIngredientIds.add(ingredient.ingredientId);
        // iterate through form
        if (!StateIngredientIds.has(ingredient.ingredientId)) {
          // ingredientId in form not in state
          // new ingredient in recipe
          requests.push(
            this.addIngredientToRecipe({ ingredient, recipeId: this.recipeId })
          );
        } else {
          // ingredientId in form and in state
          // TODO check for change?
          requests.push(
            this.editIngredientInRecipe({
              recipeId: this.recipeId,
              ingredient
            })
          );
        }
      }
      // check for ingredients that were removed
      for (const stateIngredientId of StateIngredientIds) {
        if (!formIngredientIds.has(stateIngredientId)) {
          requests.push(
            this.removeIngredientFromRecipe({
              ingredientId: stateIngredientId,
              recipeId: this.recipeId
            })
          );
        }
      }
      console.log(requests);
      if (requests.length) {
        await Promise.allSettled(requests);
      }
    },
    ...mapActions("recipe", [
      "addIngredientToRecipe",
      "editIngredientInRecipe",
      "removeIngredientFromRecipe"
    ])
  }
};
</script>

<style scoped>
.md-card {
  margin-top: 1em;
}
</style>
