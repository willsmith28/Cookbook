import requests from "../../requests/requests";

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
      const response = await requests.login(username, password);
      const { data: token } = response;

      localStorage.setItem("token", token);
      commit("SET_USER_NAME", username);
    } catch (error) {
      localStorage.removeItem("token");
      handleError(error);
    }
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
