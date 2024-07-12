<script setup>
import { RouterLink } from 'vue-router';
</script>

<template>
  <nav>
    <ul>
      <li>
        <a
          href="https://www.kth.se/cs/cst/research/vicstudio/the-visualization-studio-1.859336"
          target="_blank"
          >Om oss</a
        >
      </li>
      <li>
        <a
          href="https://www.kth.se/places/room/id/ae9e43c4-cb44-4d47-af73-895d2a8c24c6"
          target="_blank"
          title="Länk till platsinfo!:D"
          >Hitta hit</a
        >
      </li>
    </ul>
    <ul>
      <li v-if="creators && !authenticated">
        <RouterLink to="/">Hem</RouterLink>
      </li>
      <li v-if="authenticated">
        <RouterLink v-if="user.admin" to="/admin">Hem</RouterLink>
        <RouterLink v-else to="/student">Hem</RouterLink>
      </li>
      <li v-if="authenticated">
        <button id="logoutBtn" @click="logout">Logga ut</button>
      </li>
    </ul>
  </nav>
</template>

<script>
import { mapState } from 'vuex'; // Import mapState for accessing Vuex state

export default {
  data() {
    return {
      creators: false
    };
  },
  computed: {
    ...mapState(['authenticated', 'user'])
  },
  methods: {
    logout() {
      // Clear store user data and redirect to home page
      try {
        this.$store.dispatch('logoutUser');
      } catch (error) {
        console.error('Error logging out:', error);
      }
      this.$router.push('/');
    }
  },
  created() {
    // Check if the creators page is being viewed
    if (this.$route.path === '/creators') {
      this.creators = true;
    }
  }
};
</script>

<style scoped>
nav {
  display: flex;
  justify-content: space-between;
  background-color: var(--kthblue);
}

ul {
  list-style-type: none;
  padding: 0%;
  margin: 0%;
  overflow: hidden;
}

li {
  float: left;
}

#logoutBtn,
a {
  color: #eee;
  text-decoration: none;
  padding: 1rem;
  display: block;
  text-align: center;
  transition: all 0.2s;
}

a:hover {
  background-color: var(--skyblue);
}

#logoutBtn {
  font-size: unset;
  border-radius: 0;
}
</style>
