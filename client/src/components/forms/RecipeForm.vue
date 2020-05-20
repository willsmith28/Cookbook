<template>
  <div>
    <form
      class="md-layout md-gutter md-alignment-top-center"
      @submit.prevent="submitRecipe()"
    >
      <div class="md-layout-item md-size-75 md-small-size-100">
        <md-field :class="getValidationClass('name')">
          <label for="recipe-name">Name</label>
          <md-input id="recipe-name" v-model.trim="name" name="recipe-name" />
          <span v-if="!$v.name.required" class="md-error">
            This field is required
          </span>
        </md-field>
      </div>

      <div class="md-layout-item md-size-75 md-small-size-100">
        <md-field>
          <label for="description">Description</label>
          <md-textarea
            id="description"
            v-model.trim="description"
            name="description"
          />
        </md-field>
      </div>

      <div class="md-layout-item md-size-50 md-small-size-100">
        <md-field :class="getValidationClass('servings')">
          <label for="servings">Number of Servings</label>
          <md-input
            id="servings"
            v-model.number="servings"
            type="number"
            name="servings"
          />
          <span v-if="!$v.servings.required" class="md-error">
            Number of servings is required
          </span>
        </md-field>
      </div>

      <div class="md-layout-item md-size-50 md-small-size-100">
        <md-field :class="getValidationClass('cook_time')">
          <label for="cook_time">Cook Time</label>
          <md-input id="cook_time" v-model.trim="cook_time" name="cook_time" />
          <span v-if="!$v.cook_time.required" class="md-error">
            This field is required
          </span>
        </md-field>
      </div>

      <div class="md-layout-item md-size-100">
        <div class="md-layout md-alignment-left">
          <div class="md-layout-item">
            <md-button class="md-raised md-primary" @click="validateRecipe()">
              {{ recipeId ? "Edit" : "Create" }} Recipe
            </md-button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
export default {
  name: "RecipeForm",
  mixins: [validationMixin],
  props: {
    recipeId: { type: [Number, String], default: null }
  },
  data: () => ({
    name: null,
    description: null,
    servings: null,
    cook_time: null
  }),
  validations: {
    name: { required },
    description: { required },
    servings: { required },
    cook_time: { required }
  },
  computed: {
    ...mapGetters("recipe", ["getRecipe"])
  },
  created() {
    if (this.recipeId) {
      const { name, description, servings, cook_time } = this.getRecipe(
        this.recipeId
      );
      this.name = name;
      this.description = description;
      this.servings = servings;
      this.cook_time = cook_time;
    }
  },
  methods: {
    getValidationClass(fieldName) {
      const { [fieldName]: field } = this.$v;
      if (field) {
        return { "md-invalid": field.$invalid && field.$dirty };
      }
    },
    submitRecipe() {},
    validateRecipe() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.submitRecipe();
      }
    }
  }
};
</script>

<style></style>
