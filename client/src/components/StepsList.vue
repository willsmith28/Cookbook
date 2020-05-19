<template>
  <div>
    <ol>
      <li v-for="(instruction, stepIndex) of steps" :key="stepIndex">
        <p>
          {{ instruction }}
        </p>
      </li>
    </ol>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "StepsList",
  props: { recipeId: { type: [String, Number], required: true } },
  computed: {
    steps() {
      const steps = this.getSteps(this.recipeId);
      return steps ? steps : [];
    },
    ...mapGetters("recipe", ["getSteps"])
  }
};
</script>

<style>
ol {
  display: inline-block;
  text-align: left;
}
div {
  text-align: center;
}
</style>
