<template>
  <main>
    <header>
      <h1 v-if="authenticated">Du är inloggad</h1>
      <h1 v-else>Logga in</h1>
    </header>
    <div v-if="authenticated" class="loginPanel">
      <div class="inputs">
        <button @click="logout">Logga ut</button>
      </div>
    </div>
    <div v-else-if="!create" class="loginPanel">
      <div class="inputs">
        <input
          id="email"
          :class="{ error: error }"
          type="text"
          placeholder="E-postadress"
          v-model="email"
          @blur="validateEmail"
        />
        <button @click="login">Logga in</button>
      </div>
      <button
        @click="
          () => {
            this.create = true;
          }
        "
      >
        Skapa nytt konto
      </button>
    </div>
    <div v-if="create" class="loginPanel">
      <div id="create" class="inputs">
        <input
          id="email"
          :class="{ error: emailError }"
          type="text"
          placeholder="E-postadress"
          v-model="email"
          @blur="validateEmail"
        />
        <input
          id="newName"
          :class="{ error: nameError }"
          type="text"
          placeholder="För- och efternamn"
          v-model="newName"
          @blur="validateName"
        />
        <div class="buttonRow">
          <button
            @click="
              () => {
                this.create = false;
              }
            "
          >
            Tillbaka
          </button>
          <button @click="createUser">Skapa användare</button>
        </div>
      </div>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </main>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests
import { mapState } from 'vuex'; // Import mapState for accessing Vuex state

export default {
  name: 'LoginView',
  computed: {
    ...mapState(['authenticated', 'user'])
  },
  data() {
    return {
      email: '',
      error: '',
      create: false,
      newName: '',
      emailError: false,
      nameError: false
    };
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
    },
    async login() {
      try {
        this.error = ''; // Clear any previous error messages

        // Validate email format before sending the request
        if (!this.validateEmail()) {
          this.error = 'Ogiltig e-postadress.';
          console.error('Invalid email:', this.email);
          return; // Don't proceed with login if email is invalid
        }

        const response = await axios.post(
          SERVER_URL + '/api/login',
          {
            email: this.email
          },
          {
            withCredentials: true
          }
        );

        if (response.data) {
          // Login successful7
          this.$store.commit('setAuthenticated', true); // Set authenticated to true
          this.$store.commit('setUser', response.data); // Set user data in store

          // Redirect to the appropriate page based on user permission
          if (response.data.admin) {
            this.$router.push('/admin');
          } else {
            this.$router.push('/student');
          }
        } else {
          this.error = response.data.message || 'Login failed. Server error.';
          console.error('Login failed:', response);
        }
      } catch (error) {
        console.error('Error logging in:', error);
        if (error.response.status === 404) {
          this.error = 'E-postadressen finns inte i systemet.';
        } else {
          this.error = error.response.data.message || 'Login failed. Server error.';
        }
      }
    },

    validateEmail() {
      if (this.email.indexOf('@') === -1 || this.email.indexOf('.') === -1) {
        this.emailError = true;
        return false;
      } else {
        this.emailError = false;
        return true;
      }
    },
    validateName() {
      if (this.newName.length < 3) {
        this.nameError = true;
        return false;
      } else {
        this.nameError = false;
        return true;
      }
    },

    async createUser() {
      try {
        this.error = ''; // Clear any previous error messages

        // Validate email format before sending the request
        if (!this.validateEmail()) {
          this.error = 'Ogiltig e-postadress.';
          console.error('Invalid email:', this.email);
          return; // Don't proceed with login if email is invalid
        }

        // Validate name
        if (!this.validateName()) {
          this.error = 'Namnet måste vara minst 2 tecken.';
          console.error('Invalid name:', this.name);
          return; // Don't proceed with login if name is invalid
        }

        const response = await axios.post(
          SERVER_URL + `/api/user`,
          {
            email: this.email,
            name: this.newName,
            admin: false
          },
          {
            withCredentials: true
          }
        );

        if (response.status === 200 && response.data) {
          console.log('User created:', response.data);
          // Redirect to student page
          const user = response.data.user;
          this.$store.commit('setAuthenticated', true); // Set authenticated to true
          this.$store.commit('setUser', user); // Set user data in store
          this.$router.push('/student');
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
.loginPanel {
  width: 30rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.inputs {
  min-width: fit-content;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

#create {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.buttonRow {
  display: flex;
  flex-direction: row;
  gap: 1rem;
}
</style>
