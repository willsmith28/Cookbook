<template>
  <md-select
    id="unit"
    v-model="value"
    name="unit"
    required
    @md-selected="$emit('input', $event)"
  >
    <md-optgroup
      v-for="(unitGroup, groupIndex) of ingredientUnits"
      :key="groupIndex"
      :label="unitGroup[0]"
    >
      <md-option
        v-for="(unitText, unitIndex) of unitGroup[1]"
        :key="unitIndex"
        :value="unitText"
      >
        {{ unitText }}
      </md-option>
    </md-optgroup>
  </md-select>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "IngredientUnitSelect",
  props: { value: { type: String, required: true, default: null } },
  computed: {
    ...mapGetters("recipe", ["ingredientUnits"])
  }
};
</script>
