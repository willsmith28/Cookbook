<template>
  <div>
    <md-steppers md-sync-route md-dynamic-height>
      <md-step
        id="first"
        :to="
          recipeId
            ? { name: 'recipe-edit', params: { recipeId } }
            : { name: 'recipe-create' }
        "
        :md-label="`${recipeId ? 'Edit' : 'Create'} Recipe`"
        exact
      >
        <recipe-form :recipe-id="recipeId" />
      </md-step>
      <md-step
        id="second"
        :to="
          recipeId
            ? { name: 'recipe-edit-ingredients', params: { recipeId } }
            : null
        "
        md-label="Edit Ingredients"
        :md-editable="recipeId"
        exact
      >
        <ingredient-in-recipe-form v-if="recipeId" :recipe-id="recipeId" />
      </md-step>
      <md-step
        id="third"
        :to="
          recipeId ? { name: 'recipe-edit-steps', params: { recipeId } } : null
        "
        md-label="Edit Steps"
        :md-editable="recipeId"
        exact
      ></md-step>
    </md-steppers>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import RecipeForm from "@/components/forms/RecipeForm";
import IngredientInRecipeForm from "@/components/forms/IngredientInRecipeForm";
export default {
  components: { RecipeForm, IngredientInRecipeForm },
  mixins: [validationMixin],
  props: { recipeId: { type: [String, Number], default: null } },
  data() {
    return {
      formData: {
        ingredients: [],
        steps: [],
        tags: []
      }
    };
  },
  validations: {
    formData: {
      ingredients: {
        $each: {
          amount: { required },
          unit: { required },
          ingredient_id: { required },
          specifier: {}
        }
      },
      steps: {
        $each: {
          instruction: { required }
        }
      },
      tags: {
        $each: { value: { required }, kind: { required } }
      }
    }
  },
  computed: {
    ...mapGetters("recipe", [
      "ingredients",
      "ingredientUnits",
      "getRecipe",
      "getIngredientsInRecipe",
      "getSteps"
    ])
  },
  methods: {
    getValidationClass(fieldName) {
      const field = this.$v.formData[fieldName];
      if (field) {
        return { "md-invalid": field.$invalid && field.$dirty };
      }
    },
    addIngredient() {
      this.ingredients.push({
        amount: null,
        unit: null,
        ingredientId: null,
        specifier: null
      });
    },
    removeIngredient(index) {
      this.ingredients.splice(index, 1);
    },
    ...mapActions("recipe", ["fetchIngredientUnits"])
  }
};
</script>
