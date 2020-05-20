import client from "./client";

const requests = {
  login(username, password) {
    return client.post("/auth/", {
      username,
      password
    });
  },

  getUserInfo() {
    return client.get("/user/me/");
  },

  getAllIngredients() {
    return client.get("/recipe-manager/ingredient/");
  },

  getIngredientUnits() {
    return client.get("/recipe-manager/ingredient/units/");
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

  getTagKinds() {
    return client.get("/recipe-manager/tag/kind/");
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

  editRecipe(recipe_id, recipe) {
    return client.put(`/recipe-manager/recipe/${recipe_id}/`, recipe);
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

  getStepInRecipe(recipe_id, order) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/steps/${order}/`);
  },

  editStepInRecipe(recipe_id, step) {
    return client.put(
      `/recipe-manager/recipe/${recipe_id}/steps/${step.order}/`,
      step
    );
  },

  removeStepFromRecipe(recipe_id, order) {
    return client.delete(`/recipe-manager/recipe/${recipe_id}/steps/${order}/`);
  },

  getAllTagsInRecipe(recipe_id) {
    return client.get(`/recipe-manager/recipe/${recipe_id}/tags/`);
  },

  addTagToRecipe(recipe_id, tag) {
    return client.post(`/recipe-manager/recipe/${recipe_id}/tags/`, tag);
  },

  removeTagFromRecipe(recipe_id, tag_id) {
    return client.delete(`/recipe-manager/recipe/${recipe_id}/tags/${tag_id}/`);
  }
};

export default requests;
