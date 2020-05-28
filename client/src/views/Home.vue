<template>
  <div class="home md-layout md-alignment-top-center">
    <recipe-overview-card
      v-for="(recipeId, index) in recipeIDs"
      :key="index"
      class="md-layout-item md-small-size-95 md-medium-size-33"
      :recipe-id="recipeId"
      hover
    />
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import RecipeOverviewCard from "@/components/RecipeOverviewCard";
export default {
  name: "Home",
  components: { RecipeOverviewCard },
  computed: {
    ...mapGetters("recipe", ["recipeIDs"])
  },
  created() {
    this.fetchAllRecipes();
  },
  methods: {
    ...mapActions("recipe", [
      "fetchAllRecipes",
      "fetchAllIngredients",
      "fetchAllTags"
    ])
  }
};
</script>

<style scoped>
.recipe-overview-card {
  margin-top: 1em;
}
</style>
