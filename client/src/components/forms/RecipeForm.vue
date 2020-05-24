<template>
  <div>
    <form @submit.prevent="submitRecipe()">
      <div>
        <md-card>
          <md-card-content class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-size-70 md-small-size-100">
              <md-field :class="getValidationClass('name')">
                <label for="name">Name</label>
                <md-input id="name" v-model.trim="name" name="name" required />
                <span v-if="!$v.name.required" class="md-error">
                  Name is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-size-70 md-small-size-100">
              <md-field>
                <label for="description">Description</label>
                <md-textarea
                  id="description"
                  v-model.trim="description"
                  name="description"
                  required
                />
                <span v-if="!$v.description.required" class="md-error">
                  Description is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-size-35 md-small-size-100">
              <md-field :class="getValidationClass('servings')">
                <label for="servings">Number of Servings</label>
                <md-input
                  id="servings"
                  v-model.number="servings"
                  type="number"
                  name="servings"
                  required
                />
                <span v-if="!$v.servings.required" class="md-error">
                  Number of servings is required
                </span>
                <span v-if="!$v.servings.positive" class="md-error">
                  Number of servings must be positive
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-size-35 md-small-size-100">
              <md-field :class="getValidationClass('cook_time')">
                <label for="cook_time">Cook Time</label>
                <md-input
                  id="cook_time"
                  v-model.trim="cook_time"
                  name="cook_time"
                  required
                />
                <span v-if="!$v.cook_time.required" class="md-error">
                  Cook Time is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-size-100">
              <div class="md-layout md-alignment-left">
                <div class="md-layout-item">
                  <md-button
                    class="md-raised md-primary"
                    @click="validateRecipe()"
                  >
                    {{ recipeId ? "Edit" : "Create" }} Recipe
                  </md-button>
                </div>
              </div>
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
    servings: { required, positive: value => value > 0 },
    cook_time: { required }
  },
  computed: {
    ...mapGetters("recipe", ["getRecipe"])
  },
  created() {
    console.log("recipe form");
    if (this.recipeId) {
      const recipe = this.getRecipe(this.recipeId);
      if (recipe) {
        this.name = recipe.name;
        this.description = recipe.description;
        this.servings = recipe.servings;
        this.cook_time = recipe.cook_time;
      }
    }
  },
  methods: {
    getValidationClass(fieldName) {
      const { [fieldName]: field } = this.$v;
      if (field) {
        return { "md-invalid": field.$invalid && field.$dirty };
      }
    },
    validateRecipe() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.submitRecipe();
      }
    },
    async submitRecipe() {
      try {
        const recipe = {
          name: this.name,
          description: this.description,
          servings: this.servings,
          cook_time: this.cook_time
        };
        let recipeId = this.recipeId;
        if (recipeId) {
          await this.editRecipe({
            recipe_id: recipeId,
            recipe
          });
        } else {
          recipeId = await this.createRecipe(recipe);
        }
        this.$router.push({
          name: "recipe-edit-ingredients",
          params: { recipeId }
        });
      } catch (error) {
        //TODO show error message in snackbar or something
      }
    },
    ...mapActions("recipe", ["createRecipe", "editRecipe"])
  }
};
</script>

<style></style>
