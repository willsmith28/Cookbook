import requests from "../../requests";

const state = {
  access: null,
  refresh: null
};

const mutations = {
  SET_ACCESS_TOKEN(state, access) {
    localStorage.setItem("access", access);
    state.access = access;
  },
  SET_REFRESH_TOKEN(state, refresh) {
    localStorage.setItem("refresh", refresh);
    state.refresh = refresh;
  },
  REMOVE_TOKENS(state) {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    state.refresh = null;
    state.access = null;
  }
};

const actions = {
  async login({ commit, dispatch }, { username, password }) {
    try {
      const {
        data: { access, refresh }
      } = await requests.login(username, password);
      await dispatch("setAccessToken", access);
      await dispatch("setRefreshToken", refresh);
    } catch (error) {
      commit("REMOVE_TOKENS");
      return Promise.reject(error);
    }
  },

  async setAccessToken({ commit }, access) {
    commit("SET_ACCESS_TOKEN", access);
  },

  async setRefreshToken({ commit }, refresh) {
    commit("SET_REFRESH_TOKEN", refresh);
  },

  logout({ commit }) {
    commit("REMOVE_TOKENS");
  }
};

const getters = {
  loggedIn: state => !!state.access,
  jwt: state => state.access,
  jwtData: state =>
    state.access ? JSON.parse(atob(state.access.split(".")[0])) : null,
  username: ({ getters }) =>
    getters("jwt") ? getters("jwtData")["username"] : null,
  email: ({ getters }) => (getters("jwt") ? getters("jwtData")["email"] : null),
  isSuperUser: ({ getters }) =>
    getters("jwt") ? getters("jwtData")["is_superuser"] : null
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
