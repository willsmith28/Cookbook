import requests from "../../requests/requests";

const state = {
  recipes: [], // name as key
  steps: {},
  ingredients: {},
  tags: {}
};

const mutations = {
  ADD_INGREDIENTS_FROM_LIST(state, ingredients) {
    state.ingredients = {};
    for (const ingredient of ingredients) {
      state.ingredients[`${ingredient.id}`] = ingredient;
    }
  },

  ADD_INGREDIENT(state, ingredient) {
    state[`${ingredient.id}`] = ingredient;
  },

  ADD_TAGS_FROM_LIST(state, tags) {
    state.tags = {};
    for (const tag of tags) {
      state.tags[`${tag.id}`] = tag;
    }
  },

  ADD_RECIPES_FROM_LIST(state, recipes) {
    state.recipes = recipe;
  },

  ADD_RECIPE(state, recipe) {
    state.recipes[`${recipe.id}`] = recipe;
  },

  ADD_INGREDIENTS_TO_RECIPE(state, { recipeID, recipeIngredients }) {
    state.recipes[`${recipeID}`].ingredients = recipeIngredients;
  },

  ADD_INGREDIENT_TO_RECIPE(state, { recipeID, ingredientInRecipe }) {
    const {
      recipes: { [recipeID]: recipe }
    } = state;

    if (Object.prototype.hasOwnProperty.call(recipe, "ingredients")) {
      recipe.ingredients.push(ingredientInRecipe);
    } else {
      recipe.ingredients = [ingredientInRecipe];
    }
  },

  REMOVE_INGREDIENT_FROM_RECIPE(state, { recipeID, ingredientID }) {
    const {
      recipes: { [recipeID]: recipe }
    } = state;

    if (Object.prototype.hasOwnProperty.call(recipe, "ingredients")) {
      recipe.ingredients.splice(
        recipe.ingredients.findIndex(
          ingredient => ingredient.ingredient_id === ingredientID
        ),
        1
      );
    }
  },

  ADD_TAG_TO_RECIPE(state, { recipeID, tag }) {
    const {
      recipes: { [recipeID]: recipe }
    } = state;

    if (Object.prototype.hasOwnProperty.call(recipe, "tags")) {
      recipe.tags.push(tag);
    } else {
      recipe.tags = [tag];
    }
  },

  REMOVE_TAG_FROM_RECIPE(state, { recipeID, tagID }) {
    const {
      recipes: { [recipeID]: recipe }
    } = state;

    if (Object.prototype.hasOwnProperty.call(recipe, "tags")) {
      recipe.tags.splice(
        recipe.tags.findIndex(tag => tag.id === tagID),
        1
      );
    }
  }
};

const actions = {
  async fetchAllRecipes({ commit }) {
    try {
      const response = await requests.getAllRecipes();
      commit("ADD_RECIPES_FROM_LIST", response.data);
    } catch (error) {
      // TODO revisit this
      handleError(error);
    }
  },

  async fetchRecipe({ commit }, recipeID) {
    try {
      const response = await requests.getRecipe(recipeID);
      commit("ADD_RECIPE", response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async createRecipe({ commit }, recipe) {
    try {
      const response = await requests.createRecipe(recipe);
      commit("ADD_RECIPE", response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async addIngredientToRecipe({ commit }, { recipeID, ingredient }) {
    try {
      const response = await requests.AddIngredientToRecipe(
        recipeID,
        ingredient
      );
      commit("ADD_INGREDIENT_TO_RECIPE", recipeID, response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async removeIngredientFromRecipe({ commit }, { recipeID, ingredientID }) {
    try {
      await requests.removeIngredientFromRecipe(recipeID, ingredientID);
      commit("REMOVE_INGREDIENT_FROM_RECIPE", recipeID, ingredientID);
    } catch (error) {
      handleError(error);
    }
  },

  async addTagToRecipe({ commit }, { recipeID, tag }) {
    try {
      const response = await requests.addTagToRecipe(recipeID, tag);
      commit("ADD_TAG_TO_RECIPE", recipeID, response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async removeTagFromRecipe({ commit }, { recipeID, tagID }) {
    try {
      await requests.removeTagFromRecipe(recipeID, tagID);
      commit("REMOVE_TAG_FROM_RECIPE", recipeID, tagID);
    } catch (error) {
      handleError(error);
    }
  },

  async fetchAllIngredients({ commit }) {
    try {
      const response = await requests.getAllIngredients();
      commit("ADD_INGREDIENTS_FROM_LIST", response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async createIngredient({ commit }, ingredient) {
    try {
      const response = requests.createIngredient(ingredient);
      commit("ADD_INGREDIENT", response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async fetchAllTags({ commit }) {
    try {
      const response = await requests.getAllTags();
      commit("ADD_TAGS_FROM_LIST", response.data);
    } catch (error) {
      handleError(error);
    }
  },

  async createTag({ commit }, tag) {
    try {
      const response = await requests.createTag(tag);
      commit("ADD_TAG", response.data);
    } catch (error) {
      handleError(error);
    }
  }
};

const getters = {
  isIngredientCached: state => name => {
    const { ingredients } = state;
    return Object.prototype.hasOwnProperty.call(ingredients, name);
  },

  getIngredientByName: state => name => {
    const { ingredients } = state;
    return ingredients[`${name}`];
  },

  ingredientCacheCount(state) {
    return Object.keys(state.ingredients).length;
  },

  isTagCached: state => value => {
    const { tags } = state;
    return Object.prototype.hasOwnProperty.call(tags, value);
  },

  getTagByValue: state => value => {
    const { tags } = state;
    return tags[`${value}`];
  },

  tagCacheCount(state) {
    return Object.keys(state.tags).length;
  },

  getRecipeByID: state => id => {
    const { recipes } = state;
    return recipes[`${id}`];
  },

  isRecipeCached: state => id => {
    const { recipes } = state;
    return Object.prototype.hasOwnProperty.call(recipes, id);
  },

  recipeCacheCount(state) {
    return Object.keys(state.recipes).length;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};

function handleError(error) {
  if (error.response) {
    // eslint-disable-next-line no-console
    console.log(error.response.data);
  } else if (error.request) {
    // eslint-disable-next-line no-console
    console.log(error.request);
  } else {
    // eslint-disable-next-line no-console
    console.log("Error", error.message);
  }
  // eslint-disable-next-line no-console
  console.log(error.config);
}
