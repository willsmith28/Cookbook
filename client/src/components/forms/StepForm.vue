<template>
  <div>
    <form novalidate @submit.prevent="validateForm()">
      <div class="md-layout md-gutter md-alignment-top-center">
        <md-card
          v-for="($step, stepIndex) of $v.steps.$each.$iter"
          :key="stepIndex"
          class="md-layout-item md-size-100"
        >
          <md-card-content class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-size-100">
              <md-field :class="getValidationClass('instruction', $step)">
                <label for="instruction">Instruction</label>
                <md-textarea
                  id="instruction"
                  v-model="$step.instruction.$model"
                  name="instruction"
                />
                <span v-show="!$step.instruction.required" class="md-error">
                  Instruction is required
                </span>
              </md-field>
            </div>
          </md-card-content>

          <md-card-actions v-if="stepIndex === steps.length - 1">
            <md-button class="secondary" @click="popStepFromForm()">
              Remove Step
            </md-button>
          </md-card-actions>
        </md-card>
        <div class="md-layout-item md-size-100 md-layout md-alignment-top-left">
          <div class="md-layout-item">
            <md-button class="md-primary md-raised" type="submit">
              Save Steps
            </md-button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import getValidationClass from "@/validations/getValidationClass";
export default {
  name: "StepForm",
  mixins: [validationMixin],
  props: {
    recipeId: { type: [String, Number], required: true }
  },
  data: () => ({ steps: [{ instruction: null }] }),
  validations: {
    steps: {
      required,
      minLength: minLength(1),
      $each: {
        instruction: { required }
      }
    }
  },
  computed: {
    ...mapGetters("recipe", ["getSteps"])
  },
  created() {
    const stepsInRecipe = this.getSteps(this.recipeId);
    if (stepsInRecipe.length) {
      this.steps = stepsInRecipe;
    }
  },
  methods: {
    getValidationClass(fieldName, $step) {
      return getValidationClass(fieldName, $step);
    },
    addStepToForm() {
      this.steps.push({ instruction: null });
    },
    popStepFromForm(stepIndex) {
      this.steps.splice(stepIndex, 1);
    },
    validateForm() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.submitForm();
      }
    },
    async submitForm() {
      const editRequests = [];
      let stateSteps = this.getSteps(this.recipeId);

      //first remove steps
      if (stateSteps.length > this.steps.length) {
        const numberToDelete = stateSteps.length - this.steps.length;
        for (let i = 0; i < numberToDelete; i++) {
          await this.removeLastStepFromRecipe(this.recipeId);
        }
        stateSteps = this.getSteps(this.recipeId);
      }

      for (const [stepIndex, step] of this.steps.entries()) {
        const stateStep = stateSteps[stepIndex];
        if (stateStep) {
          if (stateStep.instruction != step.instruction) {
            editRequests.push(
              this.editStepInRecipe({
                recipeId: this.recipeId,
                order: stepIndex + 1,
                step
              })
            );
          }
        } else {
          await this.addStepToRecipe({ recipeId: this.recipeId, step });
        }
      }

      if (editRequests.length) {
        Promise.allSettled(editRequests);
      }
      this.$router.push({
        name: "recipe-detail",
        params: { id: this.recipeId }
      });
    },
    ...mapActions("recipe", [
      "addStepToRecipe",
      "editStepInRecipe",
      "removeLastStepFromRecipe"
    ])
  }
};
</script>
