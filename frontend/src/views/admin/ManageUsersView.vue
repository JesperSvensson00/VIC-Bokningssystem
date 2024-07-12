<template>
  <div v-if="submenu == 'createUser'" class="panel">
    <h2>Skapa användare</h2>
    <CreateUserView></CreateUserView>
  </div>
  <div v-else class="panel">
    <h2>Hantera användare</h2>
    <AllUsersView></AllUsersView>
  </div>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests
import CreateUserView from './CreateUserView.vue';
import AllUsersView from './AllUsersView.vue';

export default {
  name: 'ManageUsersView',
  props: {
    submenu: String
  },
  components: {
    CreateUserView,
    AllUsersView
  },
  data() {
    return {
      query: '',
      error: '',
      success: false
    };
  },
  methods: {
    async remove() {
      try {
        this.error = ''; // Clear any previous error messages

        if (this.query == '') {
          this.error = 'Ogiltig id eller e-postadress.';
          console.error('Invalid query:', this.email);
          return; // Don't proceed with login if email is invalid
        }

        const response = await axios.delete(SERVER_URL + '/api/user/' + this.query, {
          withCredentials: true
        });

        if (response.status === 200 && response.data) {
          this.success = true;
        } else {
          console.error('Login failed:', response);
          this.error = response.data.message || 'Login failed. Server error.';
        }
      } catch (error) {
        console.error('Error logging in:', error);
        if (error.response && error.response.data) {
          this.error = error.response.data.detail || 'An error occurred. Please try again.';
        } else {
          this.error = 'An error occurred. Please try again.';
        }
      }
    }
  }
};
</script>

<style scoped>
.createUserPanel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin: 1rem;
}
.inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.adminCheck {
  display: flex;
  gap: 1rem;
}
</style>
