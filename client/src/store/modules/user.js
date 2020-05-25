import requests from "../../requests";
import router from "../../router";

const state = {
  user: null
};

const mutations = {
  SET_USER_FROM_TOKEN(state, token) {
    const userJson = atob(token.split(".")[0]);
    localStorage.setItem("user", userJson);
    state.user = JSON.parse(atob(token.split(".")[0]));
  },
  SET_USER(state, user) {
    state.user = user;
    localStorage.setItem("user", JSON.stringify(user));
  },
  REMOVE_USER(state) {
    state.user = null;
    localStorage.removeItem("user");
  }
};

const actions = {
  async login({ commit }, { username, password }) {
    try {
      const {
        data: { access }
      } = await requests.login(username, password);
      commit("SET_USER_FROM_TOKEN", access);
    } catch (error) {
      commit("REMOVE_USER");
      return Promise.reject(error);
    }
  },

  async logout({ commit }) {
    try {
      await requests.logout();
      commit("REMOVE_USER");
    } catch (error) {
      return Promise.reject(error);
    }
  },

  async refreshToken({ commit, dispatch }) {
    try {
      const {
        data: { access }
      } = await requests.refreshTokens();
      commit("SET_USER_FROM_TOKEN", access);
    } catch (error) {
      await dispatch("logout");
      router.push({ name: "login" });
      return Promise.reject(error);
    }
  },

  async checkLocalStorageForUser({ commit }) {
    const user = localStorage.getItem("user");
    if (user) {
      commit("SET_USER", JSON.parse(user));
    }
  }
};

const getters = {
  isLoggedIn: ({ user }) => !!user,
  isSuperUser: ({ user }) => (user ? user.is_superuser : false),
  username: ({ user }) => (user ? user.username : null),
  email: ({ user }) => (user ? user.email : null)
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
