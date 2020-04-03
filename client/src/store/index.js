import Vue from "vue";
import Vuex from "vuex";
import recipe from "./modules/recipe";
import user from "./modules/user";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    recipe,
    user
  }
});
