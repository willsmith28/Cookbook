<template>
  <div>
    <form @submit.prevent="submitForm()">
      <div class="md-layout md-gutter md-alignment-top-center">
        <md-card
          v-for="($ingredient, ingredientIndex) of $v.ingredientsInRecipe.$each
            .$iter"
          :key="ingredientIndex"
          class="md-layout-item"
        >
          <md-card-content class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-small-size-50">
              <md-field :class="getValidationClass('amount')">
                <label for="amount">Amount</label>
                <md-input
                  id="amount"
                  v-model.number="$ingredient.amount.$model"
                  name="amount"
                  type="number"
                />
                <span v-show="!$ingredient.amount.required" class="md-error">
                  Amount is required
                </span>
                <span v-show="!$ingredient.amount.positive" class="md-error">
                  Amount must be positive
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-50">
              <md-field :class="getValidationClass('unit')">
                <label for="unit">Unit</label>
                <ingredient-unit-select v-model="$ingredient.unit.$model" />
                <span v-show="!$ingredient.unit.required" class="md-error">
                  Unit is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('ingredientId')">
                <ingredient-autocomplete
                  v-model="$ingredient.ingredientId.$model"
                />
                <span
                  v-show="!$ingredient.ingredientId.required"
                  class="md-error"
                >
                  Ingredient is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('specifier')">
                <label for="specifier">Specifier</label>
                <md-input
                  id="specifier"
                  v-model.trim="$ingredient.specifier.$model"
                  name="specifier"
                />
              </md-field>
            </div>
          </md-card-content>
        </md-card>
      </div>
    </form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import uniqueFieldInList from "../../validations/uniqueFieldInList";
import IngredientUnitSelect from "@/components/forms/inputs/IngredientUnitSelect";
import IngredientAutocomplete from "@/components/forms/inputs/IngredientAutocomplete";
export default {
  name: "IngredientForm",
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
        specifier: null
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
    if (ingredientsInRecipe) {
      this.ingredientsInRecipe = ingredientsInRecipe;
    }
  },
  methods: {
    getValidationClass(fieldName) {
      const { [fieldName]: field } = this.$v.ingredientsInRecipe;
      if (field) {
        return { "md-invalid": field.$invalid && field.$dirty };
      }
    },
    addIngredientToForm() {
      this.ingredientsInRecipe.push({
        amount: null,
        unit: null,
        specifier: null,
        ingredientId: null
      });
    },
    removeIngredientFromForm(index) {
      this.ingredientsInRecipe.splice(index, 1);
    },
    validateForm() {
      this.$v.touch();

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
          requests.push(this.addIngredientToRecipe(ingredient));
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
      await Promise.allSettled(requests);
    },
    ...mapActions("recipe", [
      "addIngredientToRecipe",
      "editIngredientInRecipe",
      "removeIngredientFromRecipe"
    ])
  }
};
</script>
