import client from "./client";

const requests = {
  login(username, password) {
    return client.post("/api-token-auth/", {
      username,
      password,
    });
  },

  getAllIngredients() {
    return client.get("/recipe-manager/ingredient/");
  },

  createIngredient(ingredient) {
    return client.post("/recipe-manager/ingredient/", ingredient);
  },

  getIngredient(id) {
    return client.get(`/recipe-manager/ingredient/${id}/`);
  },

  getAllTags() {
    return client.get("/recipe-manager/tag/");
  },

  createTag(tag) {
    return client.post("/recipe-manager/tag/", tag);
  },

  getTag(id) {
    return client.get(`/recipe-manager/tag/${id}/`);
  },

  getAllRecipes() {
    return client.get("/recipe-manager/recipe/");
  },

  createRecipe(recipe) {
    return client.post("/recipe-manager/recipe/", recipe);
  },

  getRecipe(id) {
    return client.get(`/recipe-manager/recipe/${id}/`);
  },

  editRecipe(recipe) {
    return client.put(`/recipe-manager/recipe/${recipe.id}/`, recipe);
  },

  getAllIngredientsInRecipe(recipe_id) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/ingredients/`);
  },

  AddIngredientToRecipe(recipe_id, ingredientInRecipe) {
    return client.post(
      `/recipe-manager/recipe/${recipe_id}/ingredients/`,
      ingredientInRecipe
    );
  },

  getIngredientInRecipe(recipe_id, ingredient_id) {
    return client.get(
      `/recipe-manager/recipe/${recipe_id}/ingredients/${ingredient_id}/`
    );
  },

  editIngredientInRecipe(ingredientInRecipe) {
    return client.put(
      `/recipe-manager/recipe/${ingredientInRecipe.recipe_id}/ingredients/${ingredientInRecipe.ingredient_id}/`,
      ingredientInRecipe
    );
  },

  removeIngredientFromRecipe(recipe_id, ingredient_id) {
    return client.delete(
      `/recipe-manager/recipe/${recipe_id}/ingredients/${ingredient_id}/`
    );
  },

  getAllStepsInRecipe(recipe_id) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/steps/`);
  },

  addStepToRecipe(recipe_id, step) {
    return client.post(`/recipe-manager/recipe/${recipe_id}/steps/`, step);
  },

  getStepInRecipe(recipe_id, step_id) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/steps/${step_id}/`);
  },

  editStepInRecipe(recipe_id, step) {
    return client.put(
      `/recipe-manager/recipe/${recipe_id}/steps/${step.id}/`,
      step
    );
  },

  removeStepFromRecipe(recipe_id, step_id) {
    return client.delete(
      `/recipe-manager/recipe/${recipe_id}/steps/${step_id}/`
    );
  },

  getAllTagsInRecipe(recipe_id) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/tags/`);
  },

  addTagToRecipe(recipe_id, tag) {
    return client.post(`/recipe-manager/recipe/${recipe_id}/tags/`, tag);
  },

  removeTagFromRecipe(recipe_id, tag_id) {
    return client.delete(`/recipe-manager/recipe/${recipe_id}/tags/${tag_id}/`);
  },
};

export default requests;
