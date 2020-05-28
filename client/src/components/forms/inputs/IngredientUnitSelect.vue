<template>
  <md-select
    id="unit"
    v-model="selectedUnit"
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
        v-for="(unit, unitIndex) of unitGroup[1]"
        :key="unitIndex"
        :value="unit[0]"
      >
        {{ unit[1] }}
      </md-option>
    </md-optgroup>
  </md-select>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
export default {
  name: "IngredientUnitSelect",
  props: { value: { type: [String], default: null } },
  data: () => ({ selectedUnit: null }),
  computed: {
    ...mapGetters("recipe", ["ingredientUnits"])
  },
  created() {
    if (!this.ingredientUnits.length) {
      this.fetchIngredientUnits();
    }
    if (this.value) {
      this.selectedUnit = this.value;
    }
  },
  methods: {
    ...mapActions("recipe", ["fetchIngredientUnits"])
  }
};
</script>
