import Vue from "vue";
import requests from "../../requests";

const state = {
  recipes: {},
  steps: {},
  ingredientsInRecipe: {},
  ingredients: {},
  tags: {},
};

// const state = {
//   recipes: {
//     '1': {
//       id: 1,
//       name: "",
//       description: "",
//       servings: 1,
//       cook_time: "",
//       created_on: "",
//       last_updated_on: "",
//       steps: [1],
//       ingredients: [1],
//       tags: [1],
//     },
//   },
//   steps: { '1': { id: 1, instruction: "", order: 1, recipe_id: 1 } },
//   ingredientsInRecipe: {
//     "1 1": { amount: "", unit: "", specifier: "", ingredient_id: 1 },
//   },
//   ingredients: { '1': { name: "", recipe_id: null } },
//   tags: { '1': { value: "" } },
// };

const mutations = {
  ADD_INGREDIENTS_FROM_LIST(state, ingredientsList) {
    // GET /ingredient/
    const ingredients = {};
    for (const ingredient of ingredientsList) {
      ingredients[`${ingredient.id}`] = ingredient;
    }
    state.ingredients = ingredients;
  },
  ADD_INGREDIENT(state, ingredient) {
    // GET /ingredient/pk/ or POST /ingredient/
    Vue.set(state.ingredients, `${ingredient.id}`, ingredient);
  },
  ADD_TAGS_FROM_LIST(state, tagsList) {
    // GET /tags/
    const tags = {};
    for (const tag of tagsList) {
      tags[`${tag.id}`] = tag;
    }
    state.tags = tags;
  },
  ADD_TAG(state, tag) {
    // GET /tag/pk/ or POST /tag/
    Vue.set(state.tags, `${tag.id}`, tag);
  },
  ADD_RECIPES_FROM_LIST(state, recipesList) {
    // GET /recipe/
    const recipes = {};
    for (const recipe of recipesList) {
      recipes[`${recipe.id}`] = recipe;
    }
    state.recipes = recipes;
  },
  ADD_RECIPE(state, recipe) {
    // GET,PUT /recipe/pk/ or POST /recipe/
    Vue.set(state.recipes, `${recipe.id}`, recipe);
  },
  ADD_INGREDIENTS_IN_RECIPE_FROM_LIST(state, ingredientInRecipeList) {
    // GET /recipe/pk/ingredients/
    for (const ingredientInRecipe of ingredientInRecipeList) {
      Vue.set(
        state.ingredientsInRecipe,
        `${ingredientInRecipe.ingredient_id} ${ingredientInRecipe.recipe_id}`,
        ingredientInRecipe
      );
    }
  },
  ADD_INGREDIENT_IN_RECIPE(state, ingredientInRecipe) {
    // POST /recipe/pk/ingredients/ or GET,PUT /recipe/pk/ingredients/pk/
    Vue.set(
      state.ingredientsInRecipe,
      `${ingredientInRecipe.ingredient_id} ${ingredientInRecipe.recipe_id}`,
      ingredientInRecipe
    );
  },
  ADD_INGREDIENT_TO_RECIPE(state, ingredientInRecipe) {
    // POST /recipe/pk/ingredients/
    const {
      recipes: { [ingredientInRecipe.recipe_id]: recipe },
    } = state;

    recipe.ingredients.push(ingredientInRecipe.ingredient_id);
  },
  REMOVE_INGREDIENT_FROM_RECIPE(state, { ingredient_id, recipe_id }) {
    // DELETE /recipe/pk/ingredients/pk/
    const {
      recipes: { [recipe_id]: recipe },
    } = state;

    recipe.ingredients.splice(recipe.ingredients.indexOf(ingredient_id), 1);
  },
  DELETE_INGREDIENT_IN_RECIPE(state, { ingredient_id, recipe_id }) {
    // DELETE /recipe/pk/ingredients/pk/
    Vue.delete(state.ingredientsInRecipe, `${ingredient_id} ${recipe_id}`);
  },
  ADD_TAG_TO_RECIPE(state, { tag_id, recipe_id }) {
    // POST /recipe/pk/tags/pk/
    const {
      recipes: { [recipe_id]: recipe },
    } = state;

    recipe.tags.push(tag_id);
  },
  REMOVE_TAG_FROM_RECIPE(state, { tag_id, recipe_id }) {
    // DELETE /recipe/pk/tags/pk/
    const {
      recipes: { [recipe_id]: recipe },
    } = state;

    recipe.tags.splice(recipe.tags.indexOf(tag_id), 1);
  },
  ADD_STEPS_FROM_LIST(state, steps) {
    // GET /recipe/pk/steps/
    for (const step of steps) {
      Vue.set(state.steps, `${step.id}`, step);
    }
  },
  ADD_STEP(state, step) {
    // GET, PUT /recipe/pk/steps/pk/ or POST /recipe/pk/steps/
    Vue.set(state.steps, `${step.id}`, step);
  },
  ADD_STEP_TO_RECIPE(state, { step_id, recipe_id }) {
    // POST /recipe/pk/steps/
    const {
      recipes: { [recipe_id]: recipe },
    } = state;

    recipe.steps.push(step_id);
  },
  REMOVE_STEP_FROM_RECIPE(state, { step_id, recipe_id }) {
    // DELETE /recipe/pk/steps/id/
    const {
      recipes: { [recipe_id]: recipe },
    } = state;

    recipe.steps.splice(recipe.steps.indexOf(step_id));
  },
  REMOVE_STEP(state, step_id) {
    // DELETE /recipe/pk/steps/id/
    Vue.delete(state.steps, `${step_id}`);
  },
};

const actions = {
  async fetchAllIngredients({ commit }) {
    // GET /ingredient/
    try {
      const { data: ingredients } = await requests.getAllIngredients();
      commit("ADD_INGREDIENTS_FROM_LIST", ingredients);
    } catch (error) {
      handleError(error);
    }
  },
  async createIngredient({ commit }, ingredient) {
    // POST /ingredient/
    try {
      const { data: createdIngredient } = requests.createIngredient(ingredient);
      commit("ADD_INGREDIENT", createdIngredient);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
    }
  },
  async fetchAllTags({ commit }) {
    // GET /tag/
    try {
      const { data: tags } = await requests.getAllTags();
      commit("ADD_TAGS_FROM_LIST", tags);
    } catch (error) {
      handleError(error);
    }
  },
  async createTag({ commit }, tag) {
    // POST /tag/
    try {
      const { data: createdSag } = await requests.createTag(tag);
      commit("ADD_TAG", createdSag);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
    }
  },
  async fetchAllRecipes({ commit }) {
    // GET /recipe/
    try {
      const { data: recipes } = await requests.getAllRecipes();
      commit("ADD_RECIPES_FROM_LIST", recipes);
    } catch (error) {
      handleError(error);
    }
  },
  async createRecipe({ commit, dispatch }, recipe) {
    // POST /recipe/
    try {
      const { data: createdRecipe } = await requests.createRecipe(recipe);
      const dispatchMethods = [];
      if (recipe.steps.length || recipe.ingredients.length) {
        if (recipe.steps.length) {
          dispatchMethods.push("fetchStepsInRecipe");
        }
        if (recipe.ingredients.length) {
          dispatchMethods.push("fetchIngredientsInRecipe");
        }
        await Promise.all(
          dispatchMethods.map((method) => dispatch(method, createdRecipe.id))
        );
      }
      commit("ADD_RECIPE", createdRecipe);
    } catch (error) {
      // TODO handle 400
      handleError(error);
    }
  },
  async fetchRecipeDetail({ commit, dispatch }, recipe_id) {
    // GET /recipe/pk/
    try {
      const { data: recipe } = await requests.getRecipe(recipe_id);
      const dispatchMethods = [];
      if (recipe.steps.length || recipe.ingredients.length) {
        if (recipe.steps.length) {
          dispatchMethods.push("fetchStepsInRecipe");
        }
        if (recipe.ingredients.length) {
          dispatchMethods.push("fetchIngredientsInRecipe");
        }
        await Promise.all(
          dispatchMethods.map((method) => dispatch(method, recipe_id))
        );
      }
      commit("ADD_RECIPE", recipe);
    } catch (error) {
      handleError(error);
    }
  },

  async editRecipe({ commit }, recipe) {
    // PUT /recipe/pk/
    try {
      const { data: changedRecipe } = await requests.editRecipe(recipe);
      commit("ADD_RECIPE", changedRecipe);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchIngredientsInRecipe({ commit }, recipe_id) {
    // GET /recipe/pk/ingredients/
    try {
      const {
        data: ingredientInRecipeList,
      } = await requests.getAllIngredientsInRecipe(recipe_id);
      commit("ADD_INGREDIENTS_IN_RECIPE_FROM_LIST", ingredientInRecipeList);
    } catch (error) {
      handleError(error);
    }
  },
  async addIngredientToRecipe({ commit }, { ingredient, recipe_id }) {
    // POST /recipe/pk/ingredients/
    try {
      const { data: ingredientInRecipe } = await requests.AddIngredientToRecipe(
        recipe_id,
        ingredient
      );
      commit("ADD_INGREDIENT_IN_RECIPE", ingredientInRecipe);
      commit("ADD_INGREDIENT_TO_RECIPE", ingredientInRecipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editIngredientInRecipe({ commit }, ingredientInRecipe) {
    // PUT /recipe/pk/ingredients/pk/
    try {
      const {
        data: changedIngredientInRecipe,
      } = await requests.editIngredientInRecipe(ingredientInRecipe);
      commit("ADD_INGREDIENT_IN_RECIPE", changedIngredientInRecipe);
    } catch (error) {
      // TODO handle 400
      handleError(error);
    }
  },
  async removeIngredientFromRecipe({ commit }, { ingredient_id, recipe_id }) {
    // DELETE /recipe/pk/ingredients/pk/
    try {
      await requests.removeIngredientFromRecipe(recipe_id, ingredient_id);
      commit("REMOVE_INGREDIENT_FROM_RECIPE", { ingredient_id, recipe_id });
      commit("DELETE_INGREDIENT_IN_RECIPE", { ingredient_id, recipe_id });
    } catch (error) {
      handleError(error);
    }
  },
  async addTagToRecipe({ commit }, { tag_id, recipe_id }) {
    // POST /recipe/pk/tags/
    try {
      await requests.addTagToRecipe(recipe_id, { id: tag_id });
      commit("ADD_TAG_TO_RECIPE", { recipe_id, tag_id });
    } catch (error) {
      handleError(error);
    }
  },
  async removeTagFromRecipe({ commit }, { tag_id, recipe_id }) {
    // DELETE /recipe/pk/tags/pk/
    try {
      await requests.removeTagFromRecipe(recipe_id, tag_id);
      commit("REMOVE_TAG_FROM_RECIPE", { tag_id, recipe_id });
    } catch (error) {
      handleError(error);
    }
  },
  async fetchStepsInRecipe({ commit }, recipe_id) {
    // GET /recipe/pk/steps/
    try {
      const { data: steps } = await requests.getAllStepsInRecipe(recipe_id);
      commit("ADD_STEPS_FROM_LIST", steps);
    } catch (error) {
      handleError(error);
    }
  },
  async addStepToRecipe({ commit }, { recipe_id, step }) {
    // POST /recipe/pk/steps/
    try {
      const { data: createdStep } = await requests.addStepToRecipe(
        recipe_id,
        step
      );
      commit("ADD_STEP", createdStep);
      commit("ADD_STEP_TO_RECIPE", { step_id: createdStep.id, recipe_id });
    } catch (error) {
      handleError(error);
    }
  },
  async editStepInRecipe({ commit }, { recipe_id, step }) {
    // PUT /recipe/pk/steps/pk/
    try {
      const { data: changedStep } = await requests.editStepInRecipe(
        recipe_id,
        step
      );
      commit("ADD_STEP", changedStep);
    } catch (error) {
      handleError(error);
    }
  },
  async removeStepFromRecipe({ commit }, { recipe_id, step_id }) {
    // DELETE /recipe/pk/steps/pk/
    try {
      await requests.removeStepFromRecipe(recipe_id, step_id);
      commit("REMOVE_STEP", { step_id, recipe_id });
      commit("REMOVE_STEP_FROM_RECIPE", { step_id, recipe_id });
    } catch (error) {
      handleError(error);
    }
  },
};

const getters = {
  getIngredient: (state) => (id) => {
    const {
      ingredients: { [id]: ingredient },
    } = state;
    return ingredient;
  },

  ingredientCount(state) {
    return Object.keys(state.ingredients).length;
  },

  getTag: (state) => (id) => {
    const {
      tags: { [id]: tag },
    } = state;
    return tag;
  },

  tagCount(state) {
    return Object.keys(state.tags).length;
  },

  getRecipe: (state) => (id) => {
    const {
      recipes: { [id]: recipe },
    } = state;
    return recipe;
  },

  recipeCount(state) {
    return Object.keys(state.recipes).length;
  },

  getIngredientInRecipe: (state) => (ingredient_id, recipe_id) => {
    const key = `${ingredient_id} ${recipe_id}`;
    const {
      ingredientsInRecipe: { [key]: ingredientInRecipe },
    } = state;
    return ingredientInRecipe;
  },

  getStep: (state) => (step_id) => {
    const {
      steps: { [`${step_id}`]: step },
    } = state;
    return step;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
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
