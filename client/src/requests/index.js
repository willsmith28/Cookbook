import client from "./client";

const requests = {
  login(username, password) {
    return client.post("/token/", {
      username,
      password
    });
  },

  refreshTokens() {
    return client.post("/token/refresh/");
  },

  logout() {
    return client.post("/token/logout/");
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

  editRecipe(recipe) {
    return client.put(`/recipe-manager/recipe/${recipe.id}/`, recipe);
  },

  getAllIngredientsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipe/${recipeId}/ingredients/`);
  },

  AddIngredientToRecipe(recipeId, { ingredientId, ...ingredientInRecipe }) {
    return client.post(`/recipe-manager/recipe/${recipeId}/ingredients/`, {
      ingredient_id: ingredientId,
      ...ingredientInRecipe
    });
  },

  getIngredientInRecipe(recipeId, ingredientId) {
    return client.get(
      `/recipe-manager/recipe/${recipeId}/ingredients/${ingredientId}/`
    );
  },

  editIngredientInRecipe(recipeId, { ingredientId, ...ingredientInRecipe }) {
    return client.put(
      `/recipe-manager/recipe/${recipeId}/ingredients/${ingredientInRecipe.ingredientId}/`,
      { ingredient_id: ingredientId, ...ingredientInRecipe }
    );
  },

  removeIngredientFromRecipe(recipeId, ingredientId) {
    return client.delete(
      `/recipe-manager/recipe/${recipeId}/ingredients/${ingredientId}/`
    );
  },

  getAllStepsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipe/${recipeId}/steps/`);
  },

  addStepToRecipe(recipeId, step) {
    return client.post(`/recipe-manager/recipe/${recipeId}/steps/`, step);
  },

  getStepInRecipe(recipeId, order) {
    return client.get(`/recipe-manager/recipe/${recipeId}/steps/${order}/`);
  },

  editStepInRecipe(recipeId, step) {
    return client.put(
      `/recipe-manager/recipe/${recipeId}/steps/${step.order}/`,
      step
    );
  },

  removeStepFromRecipe(recipeId, order) {
    return client.delete(`/recipe-manager/recipe/${recipeId}/steps/${order}/`);
  },

  getAllTagsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipe/${recipeId}/tags/`);
  },

  addTagToRecipe(recipeId, tag) {
    return client.post(`/recipe-manager/recipe/${recipeId}/tags/`, tag);
  },

  removeTagFromRecipe(recipeId, tagId) {
    return client.delete(`/recipe-manager/recipe/${recipeId}/tags/${tagId}/`);
  }
};

export default requests;
