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
    return client.get("/recipe-manager/ingredients/");
  },

  getIngredientUnits() {
    return client.get("/recipe-manager/ingredients/units/");
  },

  createIngredient({ recipeId, ...ingredient }) {
    return client.post("/recipe-manager/ingredients/", {
      recipe_id: recipeId,
      ...ingredient
    });
  },

  getIngredient(id) {
    return client.get(`/recipe-manager/ingredients/${id}/`);
  },

  getAllTags() {
    return client.get("/recipe-manager/tags/");
  },

  createTag(tag) {
    return client.post("/recipe-manager/tags/", tag);
  },

  getTag(id) {
    return client.get(`/recipe-manager/tags/${id}/`);
  },

  getTagKinds() {
    return client.get("/recipe-manager/tags/kind/");
  },

  getAllRecipes() {
    return client.get("/recipe-manager/recipes/");
  },

  createRecipe(recipe) {
    return client.post("/recipe-manager/recipes/", recipe);
  },

  getRecipe(id) {
    return client.get(`/recipe-manager/recipes/${id}/`);
  },

  editRecipe(recipe) {
    return client.put(`/recipe-manager/recipes/${recipe.id}/`, recipe);
  },

  getAllIngredientsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipes/${recipeId}/ingredients/`);
  },

  AddIngredientToRecipe(recipeId, { ingredientId, ...ingredientInRecipe }) {
    return client.post(`/recipe-manager/recipes/${recipeId}/ingredients/`, {
      ingredient_id: ingredientId,
      ...ingredientInRecipe
    });
  },

  getIngredientInRecipe(recipeId, ingredientId) {
    return client.get(
      `/recipe-manager/recipes/${recipeId}/ingredients/${ingredientId}/`
    );
  },

  editIngredientInRecipe(recipeId, { ingredientId, ...ingredientInRecipe }) {
    return client.put(
      `/recipe-manager/recipes/${recipeId}/ingredients/${ingredientId}/`,
      { ingredient_id: ingredientId, ...ingredientInRecipe }
    );
  },

  removeIngredientFromRecipe(recipeId, ingredientId) {
    return client.delete(
      `/recipe-manager/recipes/${recipeId}/ingredients/${ingredientId}/`
    );
  },

  getAllStepsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipes/${recipeId}/steps/`);
  },

  addStepToRecipe(recipeId, step) {
    return client.post(`/recipe-manager/recipes/${recipeId}/steps/`, step);
  },

  getStepInRecipe(recipeId, order) {
    return client.get(`/recipe-manager/recipes/${recipeId}/steps/${order}/`);
  },

  editStepInRecipe(recipeId, order, step) {
    return client.put(
      `/recipe-manager/recipes/${recipeId}/steps/${order}/`,
      step
    );
  },

  removeStepFromRecipe(recipeId, order) {
    return client.delete(`/recipe-manager/recipes/${recipeId}/steps/${order}/`);
  },

  getAllTagsInRecipe(recipeId) {
    return client.get(`/recipe-manager/recipes/${recipeId}/tags/`);
  },

  addTagToRecipe(recipeId, tag) {
    return client.post(`/recipe-manager/recipes/${recipeId}/tags/`, tag);
  },

  removeTagFromRecipe(recipeId, tagId) {
    return client.delete(`/recipe-manager/recipes/${recipeId}/tags/${tagId}/`);
  }
};

export default requests;
