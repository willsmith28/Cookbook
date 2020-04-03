import client from "./client";

const requests = {
  login(username, password) {
    return client.post("/api-token-auth/", {
      username,
      password
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

  editRecipe(id, recipe) {
    return client.put(`/recipe-manager/recipe/${id}/`, recipe);
  },

  getAllIngredientsInRecipe(recipeID) {
    return client.get(`/recipe-manager/recipe/${recipeID}/ingredients/`);
  },

  AddIngredientToRecipe(recipeID, ingredient) {
    return client.post(
      `/recipe-manager/recipe/${recipeID}/ingredients/`,
      ingredient
    );
  },

  getIngredientInRecipe(recipeID, ingredientID) {
    return client.get(
      `/recipe-manager/recipe/${recipeID}/ingredients/${ingredientID}/`
    );
  },

  editIngredientInRecipe(recipeID, ingredientID, ingredient) {
    return client.put(
      `/recipe-manager/recipe/${recipeID}/ingredients/${ingredientID}/`,
      ingredient
    );
  },

  removeIngredientFromRecipe(recipeID, ingredientID) {
    return client.delete(
      `/recipe-manager/recipe/${recipeID}/ingredients/${ingredientID}/`
    );
  },

  getAllTagsInRecipe(recipeID) {
    return client.get(`/recipe-manager/recipe/${recipeID}/tags/`);
  },

  addTagToRecipe(recipeID, tag) {
    return client.post(`/recipe-manager/recipe/${recipeID}/tags/`, tag);
  },

  removeTagFromRecipe(recipeID, tagId) {
    return client.delete(`/recipe-manager/recipe/${recipeID}/tags/${tagId}/`);
  }
};

export default requests;
