import Vue from "vue";
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
    // GET /ingredient/
    const ingredients = {};
    for (const { recipe_id, ...ingredient } of ingredientsList) {
      ingredients[`${ingredient.id}`] = {
        recipeId: recipe_id,
        ...ingredient
      };
    }
    state.ingredients = ingredients;
  },
  ADD_INGREDIENT(state, { recipe_id, ...ingredient }) {
    // GET /ingredient/pk/ or POST /ingredient/
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
  ADD_TAG_KINDS(state, kinds) {
    state.tagKinds = kinds;
  },
  ADD_RECIPE(state, recipe) {
    // GET,PUT /recipe/pk/ or GET, POST /recipe/
    Vue.set(state.recipes, `${recipe.id}`, recipe);
  },
  ADD_INGREDIENTS_IN_RECIPE_FROM_LIST(
    state,
    { recipeId, ingredientsInRecipeList }
  ) {
    const ingredientsInRecipe = {};

    for (const {
      ingredient_id,
      ...ingredientInRecipe
    } of ingredientsInRecipeList) {
      ingredientsInRecipe[`${ingredient_id}`] = {
        ingredientId: ingredient_id,
        ...ingredientInRecipe
      };
    }

    Vue.set(state.ingredientsInRecipe, `${recipeId}`, ingredientsInRecipe);
  },
  ADD_INGREDIENT_IN_RECIPE(
    state,
    { recipeId, ingredientInRecipe: { ingredient_id, ...ingredientInRecipe } }
  ) {
    // GET, POST /recipe/pk/ingredients/ or GET,PUT /recipe/pk/ingredients/pk/
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
  REMOVE_INGREDIENT_FROM_RECIPE(
    { ingredientsInRecipe },
    { ingredientId, recipeId }
  ) {
    // DELETE /recipe/pk/ingredients/pk/
    const formattedRecipeId = `${recipeId}`;
    if (
      Object.prototype.hasOwnProperty.call(
        ingredientsInRecipe,
        formattedRecipeId
      )
    ) {
      Vue.delete(ingredientsInRecipe[formattedRecipeId], `${ingredientId}`);
    }
  },
  ADD_TAG_TO_RECIPE(state, { tagId, recipeId }) {
    // POST /recipe/pk/tags/pk/
    const {
      recipes: { [recipeId]: recipe }
    } = state;

    recipe.tags.push(tagId);
  },
  REMOVE_TAG_FROM_RECIPE(state, { tagId, recipeId }) {
    // DELETE /recipe/pk/tags/pk/
    const {
      recipes: { [`${recipeId}`]: recipe }
    } = state;

    recipe.tags.splice(recipe.tags.indexOf(tagId), 1);
  },
  ADD_STEPS_TO_RECIPE(state, { recipeId, steps }) {
    // GET /recipe/pk/steps/
    Vue.set(state.steps, `${recipeId}`, steps);
  },
  ADD_STEP_TO_RECIPE(state, { recipeId, instruction }) {
    // GET, PUT /recipe/pk/steps/order/ or POST /recipe/pk/steps/
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
    // DELETE /recipe/pk/steps/order/
    const {
      recipes: { [`${recipeId}`]: recipe }
    } = state;

    recipe.steps.pop();
  }
};

const actions = {
  async initState({ dispatch }) {
    try {
      await Promise.all([
        dispatch("fetchAllIngredients"),
        dispatch("fetchIngredientUnits"),
        dispatch("fetchAllTags"),
        dispatch("fetchTagKinds"),
        dispatch("fetchAllRecipes"),
        dispatch("user/checkLocalStorageForUser", undefined, { root: true })
      ]);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchAllIngredients({ commit }) {
    // GET /ingredient/
    try {
      const { data: ingredients } = await requests.getAllIngredients();
      commit("ADD_INGREDIENTS_FROM_LIST", ingredients);
    } catch (error) {
      handleError(error);
    }
  },
  async createIngredient({ commit }, { ingredient }) {
    // POST /ingredient/
    try {
      const { data: createdIngredient } = requests.createIngredient(ingredient);
      commit("ADD_INGREDIENT", createdIngredient);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
    }
  },
  async fetchIngredientUnits({ commit }) {
    // GET ingredients/units/
    try {
      const { data } = await requests.getIngredientUnits();
      const units = new Map();
      for (const [groupName, group] of data) {
        units.set(groupName, []);

        // eslint-disable-next-line no-unused-vars
        for (const [itemAbbreviation, itemName] of group.entries()) {
          units.get(groupName).push(itemAbbreviation);
        }
      }
      commit("ADD_INGREDIENT_UNITS", units);
    } catch (error) {
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
    // POST /tag/
    try {
      const { data: createdTag } = await requests.createTag(tag);
      commit("ADD_TAG", createdTag);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
    }
  },
  async addRecipeToState({ commit }, { ingredients, steps, ...recipe }) {
    commit("ADD_RECIPE", recipe);
    commit("ADD_STEPS_TO_RECIPE", { recipeId: recipe.id, steps });
    commit("ADD_INGREDIENTS_IN_RECIPE_FROM_LIST", {
      recipeId: recipe.id,
      ingredientsInRecipeList: ingredients
    });
  },
  async fetchAllRecipes({ dispatch }) {
    // GET /recipe/
    try {
      const { data: recipes } = await requests.getAllRecipes();
      await Promise.all(
        recipes.map(recipe => dispatch("addRecipeToState", recipe))
      );
    } catch (error) {
      handleError(error);
    }
  },
  async createRecipe({ dispatch }, recipe) {
    // POST /recipe/
    try {
      const { data: createdRecipe } = await requests.createRecipe(recipe);
      await dispatch("addRecipeToState", createdRecipe);
      return createdRecipe.id;
    } catch (error) {
      // TODO handle 400
      handleError(error);
      return Promise.reject(error);
    }
  },
  async fetchRecipeDetail({ dispatch }, recipeId) {
    // GET /recipe/pk/
    try {
      const { data: recipe } = await requests.getRecipe(recipeId);
      await dispatch("addRecipeToState", recipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editRecipe({ dispatch }, recipe) {
    // PUT /recipe/pk/
    try {
      const { data: changedRecipe } = await requests.editRecipe(recipe);
      await dispatch("addRecipeToState", changedRecipe);
    } catch (error) {
      handleError(error);
    }
  },
  async fetchIngredientsInRecipe({ commit }, recipeId) {
    // GET /recipe/pk/ingredients/
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
    // POST /recipe/pk/ingredients/
    try {
      const { data: ingredientInRecipe } = await requests.AddIngredientToRecipe(
        recipeId,
        ingredient
      );
      commit("ADD_INGREDIENT_TO_RECIPE", ingredientInRecipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editIngredientInRecipe({ commit }, { recipeId, ingredientInRecipe }) {
    // PUT /recipe/pk/ingredients/pk/
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
    }
  },
  async removeIngredientFromRecipe({ commit }, { ingredientId, recipeId }) {
    // DELETE /recipe/pk/ingredients/pk/
    try {
      await requests.removeIngredientFromRecipe(recipeId, ingredientId);
      commit("REMOVE_INGREDIENT_FROM_RECIPE", { ingredientId, recipeId });
    } catch (error) {
      handleError(error);
    }
  },
  async addTagToRecipe({ commit }, { tagId, recipeId }) {
    // POST /recipe/pk/tags/
    try {
      await requests.addTagToRecipe(recipeId, { id: tagId });
      commit("ADD_TAG_TO_RECIPE", { recipeId, tagId });
    } catch (error) {
      handleError(error);
    }
  },
  async removeTagFromRecipe({ commit }, { tagId, recipeId }) {
    // DELETE /recipe/pk/tags/pk/
    try {
      await requests.removeTagFromRecipe(recipeId, tagId);
      commit("REMOVE_TAG_FROM_RECIPE", { tagId, recipeId });
    } catch (error) {
      handleError(error);
    }
  },
  async fetchStepsInRecipe({ commit }, recipeId) {
    // GET /recipe/pk/steps/
    try {
      const { data: steps } = await requests.getAllStepsInRecipe(recipeId);
      commit("ADD_STEPS_TO_RECIPE", { recipeId, steps });
    } catch (error) {
      handleError(error);
    }
  },
  async addStepToRecipe({ commit }, { recipeId, step }) {
    // POST /recipe/pk/steps/
    try {
      const {
        data: { instruction }
      } = await requests.addStepToRecipe(recipeId, step);
      commit("ADD_STEP_TO_RECIPE", { recipeId, instruction });
    } catch (error) {
      handleError(error);
    }
  },
  async editStepInRecipe({ commit }, { recipeId, step }) {
    // PUT /recipe/pk/steps/pk/
    try {
      const {
        data: { order, instruction }
      } = await requests.editStepInRecipe(recipeId, step);
      commit("EDIT_STEP", { recipeId, order, instruction });
    } catch (error) {
      handleError(error);
    }
  },
  async removeLastStepFromRecipe({ commit, state }, recipeId) {
    // DELETE /recipe/pk/steps/pk/
    try {
      const {
        steps: { [`${recipeId}`]: steps }
      } = state;
      await requests.removeStepFromRecipe(recipeId, steps.length);
      commit("REMOVE_LAST_STEP_FROM_RECIPE", recipeId);
    } catch (error) {
      handleError(error);
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

  ingredients: state => Object.values(state.ingredients),

  ingredientNames: state =>
    Object.values(state.ingredients).map(ingredient => ingredient.name),

  ingredientUnits: state => [...state.ingredientUnits],

  tagKinds: state => [...state.tagKinds],

  ingredientCount: state => Object.keys(state.ingredients).length,

  getTag: state => id => {
    const {
      tags: { [`${id}`]: tag }
    } = state;
    return tag ? Object.assign({}, tag) : null;
  },

  tags: state => Object.values(state.tags),

  tagCount: state => Object.keys(state.tags).length,

  recipes: state => Object.values(state.recipes),

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
    return ingredient ? Object.values(ingredient) : [];
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
