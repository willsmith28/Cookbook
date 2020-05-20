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
//   ingredients: { "1": { name: "", recipe_id: null } },
//   ingredientsInRecipe: {
//     "1": {"1": { amount: "", unit: "", specifier: "", ingredient_id: 1 }},
//   },
//   steps: {"1": ["do thing",]}
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
  ADD_INGREDIENTS_IN_RECIPE(state, { recipe_id, ingredientsInRecipe }) {
    Vue.set(
      state.ingredientsInRecipe,
      `${recipe_id}`,
      Object.assign(
        {},
        ...ingredientsInRecipe.map(item => ({ [item.ingredient_id]: item }))
      )
    );
  },
  ADD_INGREDIENT_IN_RECIPE(state, ingredientInRecipe) {
    // GET, POST /recipe/pk/ingredients/ or GET,PUT /recipe/pk/ingredients/pk/
    const recipeID = `${ingredientInRecipe.recipe_id}`;
    if (
      !Object.prototype.hasOwnProperty.call(state.ingredientsInRecipe, recipeID)
    ) {
      Vue.set(state.ingredientsInRecipe, recipeID, {});
    }

    Vue.set(
      state.ingredientsInRecipe[recipeID],
      `${ingredientInRecipe.ingredient_id}`,
      ingredientInRecipe
    );
  },
  REMOVE_INGREDIENT_FROM_RECIPE(
    { ingredientsInRecipe },
    { ingredient_id, recipe_id }
  ) {
    // DELETE /recipe/pk/ingredients/pk/
    const recipeID = `${recipe_id}`;
    if (Object.prototype.hasOwnProperty.call(ingredientsInRecipe, recipeID)) {
      Vue.delete(ingredientsInRecipe[recipeID], `${ingredient_id}`);
    }
  },
  ADD_TAG_TO_RECIPE(state, { tag_id, recipe_id }) {
    // POST /recipe/pk/tags/pk/
    const {
      recipes: { [recipe_id]: recipe }
    } = state;

    recipe.tags.push(tag_id);
  },
  REMOVE_TAG_FROM_RECIPE(state, { tag_id, recipe_id }) {
    // DELETE /recipe/pk/tags/pk/
    const {
      recipes: { [`${recipe_id}`]: recipe }
    } = state;

    recipe.tags.splice(recipe.tags.indexOf(tag_id), 1);
  },
  ADD_STEPS_TO_RECIPE(state, { recipe_id, steps }) {
    // GET /recipe/pk/steps/
    Vue.set(state.steps, `${recipe_id}`, steps);
  },
  ADD_STEP_TO_RECIPE(state, { recipe_id, instruction }) {
    // GET, PUT /recipe/pk/steps/order/ or POST /recipe/pk/steps/
    const recipeID = `${recipe_id}`;
    if (!Object.prototype.hasOwnProperty.call(state.steps, recipeID)) {
      Vue.set(state.steps, recipeID, []);
    }
    state.steps[recipeID].push(instruction);
  },
  EDIT_STEP(state, { recipe_id, order, instruction }) {
    state.steps[`${recipe_id}`].splice(order - 1, 1, instruction);
  },
  REMOVE_LAST_STEP_FROM_RECIPE(state, recipe_id) {
    // DELETE /recipe/pk/steps/order/
    const {
      recipes: { [recipe_id]: recipe }
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
        dispatch("fetchAllRecipes")
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
  async fetchIngredientUnits({ commit }) {
    try {
      const { data: units } = await requests.getIngredientUnits();
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
  async fetchTagDetail({ commit }, tagID) {
    try {
      const { data: tag } = await requests.getTag(tagID);
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
      const { data: createdSag } = await requests.createTag(tag);
      commit("ADD_TAG", createdSag);
    } catch (error) {
      // TODO handle 400 and 409
      handleError(error);
    }
  },
  async addRecipeToState({ commit }, { ingredients, steps, ...recipe }) {
    commit("ADD_RECIPE", recipe);
    commit("ADD_STEPS_TO_RECIPE", { recipe_id: recipe.id, steps });
    commit("ADD_INGREDIENTS_IN_RECIPE", {
      recipe_id: recipe.id,
      ingredientsInRecipe: ingredients
    });
  },
  async fetchAllRecipes({ dispatch }) {
    // GET /recipe/
    try {
      const { data: recipes } = await requests.getAllRecipes();
      for (const recipe of recipes) {
        await dispatch("addRecipeToState", recipe);
      }
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
    }
  },
  async fetchRecipeDetail({ dispatch }, recipe_id) {
    // GET /recipe/pk/
    try {
      const { data: recipe } = await requests.getRecipe(recipe_id);
      await dispatch("addRecipeToState", recipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editRecipe({ dispatch }, { recipe_id, recipe }) {
    // PUT /recipe/pk/
    try {
      const { data: changedRecipe } = await requests.editRecipe(
        recipe_id,
        recipe
      );
      await dispatch("addRecipeToState", changedRecipe);
      return changedRecipe.id;
    } catch (error) {
      handleError(error);
    }
  },
  async fetchIngredientsInRecipe({ commit }, recipe_id) {
    // GET /recipe/pk/ingredients/
    try {
      const {
        data: ingredientsInRecipe
      } = await requests.getAllIngredientsInRecipe(recipe_id);
      commit("ADD_INGREDIENTS_IN_RECIPE", { recipe_id, ingredientsInRecipe });
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
      commit("ADD_INGREDIENT_TO_RECIPE", ingredientInRecipe);
    } catch (error) {
      handleError(error);
    }
  },
  async editIngredientInRecipe({ commit }, ingredientInRecipe) {
    // PUT /recipe/pk/ingredients/pk/
    try {
      const {
        data: changedIngredientInRecipe
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
      commit("ADD_STEPS_TO_RECIPE", { recipe_id, steps });
    } catch (error) {
      handleError(error);
    }
  },
  async addStepToRecipe({ commit }, { recipe_id, step }) {
    // POST /recipe/pk/steps/
    try {
      const {
        data: { instruction }
      } = await requests.addStepToRecipe(recipe_id, step);
      commit("ADD_STEP_TO_RECIPE", { recipe_id, instruction });
    } catch (error) {
      handleError(error);
    }
  },
  async editStepInRecipe({ commit }, { recipe_id, step }) {
    // PUT /recipe/pk/steps/pk/
    try {
      const {
        data: { order, instruction }
      } = await requests.editStepInRecipe(recipe_id, step);
      commit("EDIT_STEP", { recipe_id, order, instruction });
    } catch (error) {
      handleError(error);
    }
  },
  async removeLastStepFromRecipe({ commit, state }, { recipe_id }) {
    // DELETE /recipe/pk/steps/pk/
    try {
      const {
        steps: { [recipe_id]: steps }
      } = state;
      await requests.removeStepFromRecipe(recipe_id, steps.length);
      commit("REMOVE_LAST_STEP_FROM_RECIPE", recipe_id);
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
    return Object.assign({}, ingredient);
  },

  getIngredientName: state => id => {
    const {
      ingredients: {
        [`${id}`]: {
          ingredient: { name }
        }
      }
    } = state;
    return name;
  },

  ingredients: state => Object.values(state.ingredients),

  ingredientNames: state =>
    Object.values(state.ingredients).map(ingredient => ingredient.name),

  ingredientUnits(state) {
    const units = new Map();
    for (const [groupName, group] of state.ingredientUnits) {
      units.set(groupName, []);

      // eslint-disable-next-line no-unused-vars
      for (const [itemAbbreviation, itemName] of group.entries()) {
        units.get(groupName).push(itemAbbreviation);
      }
    }
    return units;
  },

  tagKinds: state => [...state.tagKinds],

  ingredientCount: state => Object.keys(state.ingredients).length,

  getTag: state => id => {
    const {
      tags: { [`${id}`]: tag }
    } = state;
    return Object.assign({}, tag);
  },

  tags: state => Object.values(state.tags),

  tagCount: state => Object.keys(state.tags).length,

  recipes: state => Object.values(state.recipes),

  recipeIDs: state => Object.keys(state.recipes),

  getRecipe: state => id => {
    const {
      recipes: { [`${id}`]: recipe }
    } = state;
    return Object.assign({}, recipe);
  },

  getRecipeName: state => id => {
    const {
      recipes: {
        [`${id}`]: {
          recipe: { name }
        }
      }
    } = state;
    return name;
  },

  recipeCount: state => Object.keys(state.recipes).length,

  getIngredientsInRecipe: state => recipe_id => {
    const {
      ingredientsInRecipe: { [`${recipe_id}`]: ingredient }
    } = state;
    return Object.values(ingredient);
  },

  ingredientInRecipeCount: state => recipe_id => {
    const {
      ingredientsInRecipe: { [`${recipe_id}`]: ingredientsInRecipe }
    } = state;
    return Object.keys(ingredientsInRecipe).length;
  },

  getSteps: state => recipe_id => {
    const {
      steps: { [`${recipe_id}`]: steps }
    } = state;
    return [...steps];
  },

  stepInRecipeCount: state => recipe_id => {
    const {
      steps: { [`${recipe_id}`]: steps }
    } = state;
    return steps.length;
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
