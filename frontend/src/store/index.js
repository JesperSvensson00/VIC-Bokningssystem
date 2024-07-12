import { createStore } from 'vuex'

// Create a new store instance.
export default createStore({
  state: {
    user: null,
    authenticated: false

  },
  getters: {
    getUser(state) {
      return state.user
    },
    getUserId(state) {
      return state.user?.id
    },
    isUserAdmin(state) {
      return state.user?.admin
    },
    getName(state) {
      return state.user?.name
    },
    isAuthenticated(state) {
      return state.authenticated
    }
  },
  mutations: {
    setUserId(state, userId) {
      state.user.id = userId
    },
    setUserAdmin(state, admin) {
      state.user.admin = admin
    },
    setName(state, name) {
      state.user.name = name
    },
    setUser(state, data) {
      state.user = data;
      localStorage.setItem('user', JSON.stringify(data));
    },
    clearUser(state) {
      state.user = null;
    },
    setAuthenticated(state, authenticated) {
      state.authenticated = authenticated
    }
  },
  actions: {
    loadUserFromLocalStorage({ commit }) {
      const user = JSON.parse(localStorage.getItem('user'));
      if (user) {
        commit('setUser', user);
        commit('setAuthenticated', true);
      }
    },
    logoutUser({ commit }) {
      try {
        commit('clearUser');
        commit('setAuthenticated', false);
        localStorage.removeItem('user');
        // Clear cookie
        document.cookie = "userId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        console.log("User logged out");
      } catch (error) {
        console.error(error);
      }
      
    }
  }
})