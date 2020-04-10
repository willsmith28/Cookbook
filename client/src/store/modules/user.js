import requests from "../../requests";

const state = {
  userName: null
};

const mutations = {
  SET_USER_NAME(state, userName) {
    state.userName = userName;
  },
  LOGOUT(state) {
    state.userName = null;
  }
};

const actions = {
  async login({ commit }, { username, password }) {
    try {
      const {
        data: { token }
      } = await requests.login(username, password);

      localStorage.setItem("token", token);
      commit("SET_USER_NAME", username);
    } catch (error) {
      localStorage.removeItem("token");
      return Promise.reject(error);
    }
  },

  setUsername({ commit }, username) {
    commit("SET_USER_NAME", username);
  },

  logout({ commit }) {
    localStorage.removeItem("token");
    commit("LOGOUT");
  }
};

const getters = {
  loggedIn(state) {
    return !!state.userName;
  },
  userName(state) {
    return state.userName;
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
