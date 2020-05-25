import Vue from "vue";
import router from "../../router";
import requests from "../../requests";

const state = {
  recipes: {},
  steps: {},
  ingredientsInRecipe: {},
  ingredients: {},
  ingredientUnits: [],
  tags: {},
  tagKinds: []
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
//       tags: [1],
//     },
//   },
//   ingredients: { "1": { name: "", recipeId: null } },
//   ingredientsInRecipe: {
//     "1": {"1": { amount: "", unit: "", specifier: "", ingredientId: 1 }},
//   },
//   steps: {"1": ["do thing",]}
//   tags: { '1': { value: "" } },
// };

const mutations = {
  ADD_INGREDIENTS_FROM_LIST(state, ingredientsList) {
    // GET /ingredients/
    state.ingredients = Object.assign(
      {},
      ...ingredientsList.map(({ recipe_id, ...ingredient }) => ({
        [ingredient.id]: { recipeId: recipe_id, ...ingredient }
      }))
    );
  },
  ADD_INGREDIENT(state, { recipe_id, ...ingredient }) {
    // GET /ingredients/pk/ or POST /ingredients/
    Vue.set(state.ingredients, `${ingredient.id}`, {
      recipeId: recipe_id,
      ...ingredient
    });
  },
  ADD_INGREDIENT_UNITS(state, units) {
    state.ingredientUnits = units;
  },
  ADD_TAGS_FROM_LIST(state, tagsList) {
    // GET /tags/
    state.tags = Object.assign({}, ...tagsList.map(tag => ({ [tag.id]: tag })));
  },
  ADD_TAG(state, tag) {
    // GET /tags/pk/ or POST /tags/
    Vue.set(state.tags, `${tag.id}`, tag);
  },
  ADD_TAG_KINDS(state, kinds) {
    state.tagKinds = kinds;
  },
  ADD_RECIPE(state, recipe) {
    addRecipeToState(state, recipe);
  },
  ADD_RECIPES_FROM_LIST(state, recipeList) {
    for (const recipe of recipeList) {
      addRecipeToState(state, recipe);
    }
  },
  ADD_INGREDIENTS_IN_RECIPE_FROM_LIST(
    state,
    { recipeId, ingredientsInRecipeList }
  ) {
    const ingredientsInRecipe = Object.assign(
      {},
      ...ingredientsInRecipeList.map(({ ingredient_id, ...ingredient }) => ({
        [ingredient_id]: { ingredientId: ingredient_id, ingredient }
      }))
    );

    Vue.set(state.ingredientsInRecipe, `${recipeId}`, ingredientsInRecipe);
  },
  ADD_INGREDIENT_IN_RECIPE(
    state,
    { recipeId, ingredientInRecipe: { ingredient_id, ...ingredientInRecipe } }
  ) {
    // GET, POST /recipes/pk/ingredients/ or GET,PUT /recipes/pk/ingredients/pk/
    const formattedRecipeId = `${recipeId}`;
    if (
      !Object.prototype.hasOwnProperty.call(
        state.ingredientsInRecipe,
        formattedRecipeId
      )
    ) {
      Vue.set(state.ingredientsInRecipe, formattedRecipeId, {});
    }

    Vue.set(state.ingredientsInRecipe[formattedRecipeId], `${ingredient_id}`, {
      ingredientId: ingredient_id,
      ...ingredientInRecipe
    });
  },
  REMOVE_INGREDIENT_FROM_RECIPE(state, { ingredientId, recipeId }) {
    // DELETE /recipes/pk/ingredients/pk/
    const formattedRecipeId = `${recipeId}`;
    if (
      Object.prototype.hasOwnProperty.call(
        state.ingredientsInRecipe,
        formattedRecipeId
      )
    ) {
      Vue.delete(
        state.ingredientsInRecipe[formattedRecipeId],
        `${ingredientId}`
      );
    }
  },
  ADD_TAG_TO_RECIPE(state, { tagId, recipeId }) {
    // POST /recipes/pk/tags/pk/
    const {
      recipes: { [recipeId]: recipe }
    } = state;
    if (recipe) {
      recipe.tags.push(tagId);
    }
  },
  REMOVE_TAG_FROM_RECIPE(state, { tagId, recipeId }) {
    // DELETE /recipes/pk/tags/pk/
    const {
      recipes: { [`${recipeId}`]: recipe }
    } = state;
    if (recipe) {
      recipe.tags.splice(recipe.tags.indexOf(tagId), 1);
    }
  },
  ADD_STEPS_TO_RECIPE(state, { recipeId, steps }) {
    // GET /recipes/pk/steps/
    Vue.set(state.steps, `${recipeId}`, steps);
  },
  ADD_STEP_TO_RECIPE(state, { recipeId, instruction }) {
    // GET, PUT /recipes/pk/steps/order/ or POST /recipes/pk/steps/
    const formattedRecipeId = `${recipeId}`;
    if (!Object.prototype.hasOwnProperty.call(state.steps, formattedRecipeId)) {
      Vue.set(state.steps, formattedRecipeId, []);
    }
    state.steps[formattedRecipeId].push(instruction);
  },
  EDIT_STEP(state, { recipeId, order, instruction }) {
    state.steps[`${recipeId}`].splice(order - 1, 1, instruction);
  },
  REMOVE_LAST_STEP_FROM_RECIPE(state, recipeId) {
    // DELETE /recipes/pk/steps/order/
    const {
      recipes: { [`${recipeId}`]: recipe }
    } = state;
    if (recipe) {
      recipe.steps.pop();
    }
  }
};

const actions = {
  async initRecipes({ dispatch }) {
    try {
      await Promise.allSettled([
        dispatch("fetchAllRecipes"),
        dispatch("fetchAllIngredients"),
        dispatch("fetchIngredientUnits"),
        dispatch("fetchAllTags"),
        dispatch("fetchTagKinds")
      ]);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchAllIngredients({ commit }) {
    // GET /ingredients/
    try {
      const { data: ingredients } = await requests.getAllIngredients();
      commit("ADD_INGREDIENTS_FROM_LIST", ingredients);
    } catch (error) {
      handleError(error);
    }
  },
  async createIngredient({ commit }, ingredient) {
    // POST /ingredients/
    try {
      const { data: createdIngredient } = await requests.createIngredient(
        ingredient
      );
      commit("ADD_INGREDIENT", createdIngredient);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchIngredientUnits({ commit }) {
    // GET ingredients/units/
    try {
      const { data } = await requests.getIngredientUnits();
      const units = new Map();
      for (const [groupName, group] of data) {
        units.set(groupName, []);
        for (const unitValues of group) {
          units.get(groupName).push(unitValues);
        }
      }
      commit("ADD_INGREDIENT_UNITS", units);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchAllTags({ commit }) {
    // GET /tags/
    try {
      const { data: tags } = await requests.getAllTags();
      commit("ADD_TAGS_FROM_LIST", tags);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchTagDetail({ commit }, tagId) {
    try {
      const { data: tag } = await requests.getTag(tagId);
      commit("ADD_TAG", tag);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchTagKinds({ commit }) {
    try {
      const { data: kinds } = await requests.getTagKinds();
      commit("ADD_TAG_KINDS", kinds);
    } catch (error) {
      handleError(error);
    }
  },
  async createTag({ commit }, tag) {
    // POST /tags/
    try {
      const { data: createdTag } = await requests.createTag(tag);
      commit("ADD_TAG", createdTag);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchAllRecipes({ commit }) {
    // GET /recipes/
    try {
      const { data: recipes } = await requests.getAllRecipes();
      commit("ADD_RECIPES_FROM_LIST", recipes);
    } catch (error) {
      handleError(error);
    }
  },
  async createRecipe({ commit }, { recipe, nextRoute }) {
    // POST /recipes/
    try {
      const { data: createdRecipe } = await requests.createRecipe(recipe);
      commit("ADD_RECIPE", createdRecipe);
      if (nextRoute) {
        router.push({
          name: nextRoute,
          params: { recipeId: createdRecipe.id }
        });
      }
    } catch (error) {
      // TODO handle 400
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchRecipeDetail({ commit }, recipeId) {
    // GET /recipes/pk/
    try {
      const { data: recipe } = await requests.getRecipe(recipeId);
      commit("ADD_RECIPE", recipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editRecipe({ commit }, recipe) {
    // PUT /recipes/pk/
    try {
      const { data: changedRecipe } = await requests.editRecipe(recipe);
      commit("ADD_RECIPE", changedRecipe);
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchIngredientsInRecipe({ commit }, recipeId) {
    // GET /recipes/pk/ingredients/
    try {
      const {
        data: ingredientsInRecipeList
      } = await requests.getAllIngredientsInRecipe(recipeId);
      commit("ADD_INGREDIENTS_IN_RECIPE_FROM_LIST", {
        recipeId,
        ingredientsInRecipeList
      });
    } catch (error) {
      handleError(error);
    }
  },
  async addIngredientToRecipe({ commit }, { ingredient, recipeId }) {
    // POST /recipes/pk/ingredients/
    try {
      const { data: ingredientInRecipe } = await requests.AddIngredientToRecipe(
        recipeId,
        ingredient
      );
      commit("ADD_INGREDIENT_TO_RECIPE", ingredientInRecipe);
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async editIngredientInRecipe({ commit }, { recipeId, ingredientInRecipe }) {
    // PUT /recipes/pk/ingredients/pk/
    try {
      const {
        data: changedIngredientInRecipe
      } = await requests.editIngredientInRecipe(recipeId, ingredientInRecipe);
      commit("ADD_INGREDIENT_IN_RECIPE", {
        recipeId,
        changedIngredientInRecipe
      });
    } catch (error) {
      // TODO handle 400
      handleError(error);
      return Promise.reject(error);
    }
  },
  async removeIngredientFromRecipe({ commit }, { ingredientId, recipeId }) {
    // DELETE /recipes/pk/ingredients/pk/
    try {
      await requests.removeIngredientFromRecipe(recipeId, ingredientId);
      commit("REMOVE_INGREDIENT_FROM_RECIPE", { ingredientId, recipeId });
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async addTagToRecipe({ commit }, { tagId, recipeId }) {
    // POST /recipes/pk/tags/
    try {
      await requests.addTagToRecipe(recipeId, { id: tagId });
      commit("ADD_TAG_TO_RECIPE", { recipeId, tagId });
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async removeTagFromRecipe({ commit }, { tagId, recipeId }) {
    // DELETE /recipes/pk/tags/pk/
    try {
      await requests.removeTagFromRecipe(recipeId, tagId);
      commit("REMOVE_TAG_FROM_RECIPE", { tagId, recipeId });
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchStepsInRecipe({ commit }, recipeId) {
    // GET /recipes/pk/steps/
    try {
      const { data: steps } = await requests.getAllStepsInRecipe(recipeId);
      commit("ADD_STEPS_TO_RECIPE", { recipeId, steps });
    } catch (error) {
      handleError(error);
    }
  },
  async addStepToRecipe({ commit }, { recipeId, step }) {
    // POST /recipes/pk/steps/
    try {
      const {
        data: { instruction }
      } = await requests.addStepToRecipe(recipeId, step);
      commit("ADD_STEP_TO_RECIPE", { recipeId, instruction });
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async editStepInRecipe({ commit }, { recipeId, order, step }) {
    // PUT /recipes/pk/steps/pk/
    try {
      const {
        data: { instruction }
      } = await requests.editStepInRecipe(recipeId, order, step);
      commit("EDIT_STEP", { recipeId, order, instruction });
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  },
  async removeLastStepFromRecipe({ commit, state }, recipeId) {
    // DELETE /recipes/pk/steps/pk/
    try {
      const {
        steps: { [`${recipeId}`]: steps }
      } = state;
      await requests.removeStepFromRecipe(recipeId, steps.length);
      commit("REMOVE_LAST_STEP_FROM_RECIPE", recipeId);
    } catch (error) {
      handleError(error);
      return Promise.reject(error);
    }
  }
};

const getters = {
  getIngredient: state => id => {
    const {
      ingredients: { [`${id}`]: ingredient }
    } = state;
    return ingredient ? Object.assign({}, ingredient) : null;
  },

  getIngredientName: state => id => {
    const {
      ingredients: { [`${id}`]: ingredient }
    } = state;
    return ingredient ? ingredient.name : null;
  },

  ingredients: state =>
    Object.values(state.ingredients).map(item => Object.assign({}, item)),

  ingredientNames: state =>
    Object.values(state.ingredients).map(ingredient => ingredient.name),

  ingredientUnits: state =>
    state.ingredientUnits ? [...state.ingredientUnits.entries()] : [],

  tagKinds: state => [...state.tagKinds],

  ingredientCount: state => Object.keys(state.ingredients).length,

  getTag: state => id => {
    const {
      tags: { [`${id}`]: tag }
    } = state;
    return tag ? Object.assign({}, tag) : null;
  },

  tags: state => Object.values(state.tags).map(item => Object.assign({}, item)),

  tagCount: state => Object.keys(state.tags).length,

  recipes: state =>
    Object.values(state.recipes).map(item => Object.assign({}, item)),

  recipeIDs: state => Object.keys(state.recipes),

  getRecipe: state => id => {
    const {
      recipes: { [`${id}`]: recipe }
    } = state;
    return recipe ? Object.assign({}, recipe) : null;
  },

  getRecipeName: state => id => {
    const {
      recipes: { [`${id}`]: recipe }
    } = state;
    return recipe ? recipe.name : null;
  },

  recipeCount: state => Object.keys(state.recipes).length,

  getIngredientsInRecipe: state => recipeId => {
    const {
      ingredientsInRecipe: { [`${recipeId}`]: ingredient }
    } = state;
    return ingredient
      ? Object.values(ingredient).map(item => Object.assign({}, item))
      : [];
  },

  ingredientInRecipeCount: state => recipeId => {
    const {
      ingredientsInRecipe: { [`${recipeId}`]: ingredientsInRecipe }
    } = state;
    return ingredientsInRecipe ? Object.keys(ingredientsInRecipe).length : 0;
  },

  getSteps: state => recipeId => {
    const {
      steps: { [`${recipeId}`]: steps }
    } = state;
    return steps ? [...steps] : [];
  },

  stepInRecipeCount: state => recipeId => {
    const {
      steps: { [`${recipeId}`]: steps }
    } = state;
    return steps ? steps.length : 0;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};

const addRecipeToState = (state, { ingredients, steps, ...recipe }) => {
  const recipeId = `${recipe.id}`;
  Vue.set(state.recipes, recipeId, recipe);
  const ingredientsInRecipe = Object.assign(
    {},
    ...ingredients.map(({ ingredient_id, ...ingredient }) => ({
      [ingredient_id]: { ingredientId: ingredient_id, ingredient }
    }))
  );
  Vue.set(state.ingredientsInRecipe, recipeId, ingredientsInRecipe);
  Vue.set(state.steps, recipeId, steps);
};

const handleError = error => {
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
};
