import requests from "../../requests";

const state = {
  user: null
};

const mutations = {
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
  async decodeJWT({ commit }, token) {
    const user = JSON.parse(atob(token.split(".")[0]));
    commit("SET_USER", user);
  },

  async login({ commit, dispatch }, { username, password }) {
    try {
      const {
        data: { access }
      } = await requests.login(username, password);
      dispatch("decodeJWT", access);
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
      const { access } = await requests.refreshTokens();
      dispatch("decodeJWT", access);
    } catch (error) {
      commit("REMOVE_USER");
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
  loggedIn: state => !!state.user,
  username: ({ state }) => (state.user ? state.user.username : null),
  email: ({ state }) => (state.user ? state.user.email : null),
  isSuperUser: ({ state }) => (state.user ? state.user.is_superuser : null)
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
