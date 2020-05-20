<template>
  <div>
    <form novalidate @submit.prevent="submit()">
      <md-steppers md-sync-route md-dynamic-height>
        <md-step
          id="first"
          :to="{ name: 'recipe-create' }"
          exact
          md-label="Create Recipe"
        >
          <recipe-form :recipe-id="recipeId" />
        </md-step>
        <md-step
          id="second"
          to="/recipe/create/ingredients"
          exact
          :md-label="`${!!recipeId ? 'Edit' : 'Add'} Ingredients`"
          class="md-layout"
        >
          <div
            v-for="(ingredient, ingredientIndex) in $v.formData.ingredients
              .$each.$iter"
            :key="ingredientIndex"
            class="md-layout-item"
          >
            <div class="md-layout md-gutter">
              <div class="md-layout-item">
                <md-field>
                  <label for="amount">Amount</label>
                  <md-input
                    id="amount"
                    v-model.number="ingredient.amount.$model"
                    type="number"
                    name="amount"
                  />
                  <span v-if="!ingredient.amount.required">
                    This field is required
                  </span>
                </md-field>
              </div>

              <div class="md-layout-item">
                <md-field>
                  <label for="unit">Unit</label>
                  <md-select
                    id="unit"
                    v-model="ingredient.unit.$model"
                    name="unit"
                  >
                    <md-optgroup
                      v-for="(groupName, group) in ingredientUnits"
                      :key="groupName"
                      :label="groupName"
                    >
                      <md-option
                        v-for="(item, itemIndex) in group"
                        :key="itemIndex"
                      >
                        {{ item }}
                      </md-option>
                    </md-optgroup>
                  </md-select>
                  <span v-if="!ingredient.unit.required">
                    This field is required
                  </span>
                </md-field>
              </div>

              <div class="md-layout-item">
                <md-autocomplete
                  v-model="ingredientName"
                  :md-options="ingredientsByName"
                  @md-selected="setIngredient"
                >
                  <label for="ingredient">Ingredient</label>

                  <template
                    slot="md-autocomplete-item"
                    slot-scope="{ item, term }"
                  >
                    <md-highlight-text :md-term="term">
                      {{ item }}
                    </md-highlight-text>
                  </template>

                  <template slot="md-autocomplete-empty" slot-scope="{ term }">
                    No ingredient matching "{{ term }}" were found.
                  </template>
                </md-autocomplete>
              </div>
            </div>
          </div>
        </md-step>
        <md-step
          id="third"
          to="/recipe/create/steps"
          exact
          :md-label="`${!!recipeId ? 'Edit' : 'Add'} Steps`"
          class="md-layout"
        ></md-step>
      </md-steppers>
    </form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import RecipeForm from "@/components/forms/RecipeForm";
export default {
  components: { RecipeForm },
  mixins: [validationMixin],
  props: { recipeId: { type: [String, Number], default: null } },
  data() {
    return {
      formData: {
        name: null,
        description: null,
        servings: null,
        cook_time: null,
        ingredients: [],
        steps: [],
        tags: []
      }
    };
  },
  validations: {
    formData: {
      name: { required },
      description: { required },
      servings: { required },
      cook_time: {
        required,
        validateCookTime: value => new RegExp("").test(value)
      },
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
    stepperPath() {
      if (this.recipeId) {
        return `/recipe/${this.recipeId}/edit`;
      } else {
        return "/recipe/create";
      }
    },
    ...mapGetters("recipe", [
      "ingredients",
      "ingredientUnits",
      "getRecipe",
      "getIngredientsInRecipe",
      "getSteps"
    ])
  },
  created() {
    console.log("component created");
    if (this.recipeId) {
      const recipe = this.getRecipe(this.recipeId);
      if (recipe) {
        const { name, description, servings, cook_time, tags } = recipe;
        const ingredients = this.getIngredientsInRecipe(this.recipeId);
        const steps = this.getSteps(this.recipeId);
        this.formData = {
          name,
          description,
          servings,
          cook_time,
          ingredients,
          steps,
          tags
        };
      }
    } else {
      this.formData.ingredients.push({
        amount: null,
        unit: null,
        ingredient_id: null,
        specifier: null
      });
      this.formData.steps.push({ instruction: null });
    }
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
        ingredient_id: null,
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
