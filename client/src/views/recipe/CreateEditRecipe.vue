<template>
  <div v-if="!loading">
    <md-steppers md-sync-route md-dynamic-height>
      <md-step
        id="first"
        :to="recipeStepLink"
        :md-label="`${id ? 'Edit' : 'Create'} Recipe`"
        exact
      >
        <recipe-form :recipe-id="id" />
      </md-step>
      <md-step
        id="second"
        :to="ingredientStepLink"
        md-label="Edit Ingredients"
        :md-editable="!!id"
        exact
      >
        <ingredient-in-recipe-form v-if="id" :recipe-id="id" />
      </md-step>
      <md-step
        id="third"
        :to="stepStepLink"
        md-label="Edit Steps"
        :md-editable="!!id"
        exact
      >
        <step-form v-if="id" :recipe-id="id" />
      </md-step>
    </md-steppers>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import RecipeForm from "@/components/forms/RecipeForm";
import IngredientInRecipeForm from "@/components/forms/IngredientInRecipeForm";
import StepForm from "@/components/forms/StepForm";
export default {
  components: { RecipeForm, IngredientInRecipeForm, StepForm },
  props: { id: { type: [String, Number], default: null } },
  data: () => ({ loading: true }),
  computed: {
    recipeStepLink() {
      return this.id
        ? { name: "recipe-edit", params: { id: this.id } }
        : { name: "recipe-create" };
    },
    ingredientStepLink() {
      return this.id
        ? { name: "recipe-edit-ingredients", params: { id: this.id } }
        : null;
    },
    stepStepLink() {
      return this.id
        ? { name: "recipe-edit-steps", params: { id: this.id } }
        : null;
    },
    ...mapGetters("recipe", ["getRecipe", "tagCount", "ingredientCount"])
  },
  created() {
    if (!this.ingredientCount) {
      this.fetchAllIngredients();
    }
    if (!this.tagCount) {
      this.fetchAllTags();
    }

    if (!this.id) {
      this.loading = false;
      return;
    }

    const recipe = this.getRecipe(this.id);
    if (recipe) {
      this.loading = false;
    } else {
      this.fetchRecipeDetail(this.id).then(() => {
        this.loading = false;
      });
    }
  },
  methods: {
    ...mapActions("recipe", [
      "fetchRecipeDetail",
      "fetchAllIngredients",
      "fetchAllTags"
    ])
  }
};
</script>
