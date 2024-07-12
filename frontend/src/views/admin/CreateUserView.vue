<template>
  <div class="createUserPanel">
    <div v-if="!success" class="inputs">
      <input
        id="newEmail"
        :class="{ error: emailError }"
        type="text"
        placeholder="E-postadress"
        v-model="newEmail"
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
      <div class="adminCheck">
        <label for="newAdmin">Admin behörigheter</label>
        <input id="newAdmin" type="checkbox" v-model="newAdmin" />
      </div>
      <button @click="create">Skapa användare</button>
    </div>
    <div v-if="success">
      <p>Användaren är skapad</p>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests

export default {
  data() {
    return {
      newEmail: '',
      newName: '',
      newAdmin: false,
      error: '',
      emailError: false,
      nameError: false,
      success: false
    };
  },
  methods: {
    validateEmail() {
      if (this.newEmail.indexOf('@') === -1 || this.newEmail.indexOf('.') === -1) {
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
    async create() {
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
            email: this.newEmail,
            name: this.newName,
            admin: this.newAdmin
          },
          {
            withCredentials: true
          }
        );

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
