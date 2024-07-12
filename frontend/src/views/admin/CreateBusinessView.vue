<template>
  <div class="createUserPanel">
    <div v-if="!success" class="inputs">
      <input
        id="name"
        :class="{ error: nameError }"
        type="text"
        placeholder="Namn"
        v-model="name"
        @blur="validateName"
      />
      <input
        id="address"
        :class="{ error: addressError }"
        type="text"
        placeholder="Adress"
        v-model="address"
        @blur="validateEmail"
      />
      <input id="info" type="text" placeholder="Info" v-model="info" />
      <button @click="create">Lägg till företag</button>
    </div>
    <div v-if="success">
      <p>Företaget är tillagt</p>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests

export default {
  data() {
    return {
      info: '',
      name: '',
      address: '',
      error: '',
      addressError: false,
      nameError: false,
      success: false
    };
  },
  methods: {
    validateAddress() {
      return true;
      // if (this.newEmail.indexOf('@') === -1 || this.newEmail.indexOf('.') === -1) {
      //   this.emailError = true;
      //   return false;
      // } else {
      //   this.emailError = false;
      //   return true;
      // }
    },
    validateName() {
      if (this.name.length < 2) {
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
        if (!this.validateAddress()) {
          this.error = 'Ogiltig adress.';
          console.error('Invalid address:', this.email);
          return; // Don't proceed with login if email is invalid
        }

        // Validate name
        if (!this.validateName()) {
          this.error = 'Namnet måste vara minst 1 tecken.';
          console.error('Invalid name:', this.name);
          return; // Don't proceed with login if name is invalid
        }

        const response = await axios.post(
          SERVER_URL + `/api/business`,
          {
            name: this.name,
            info: this.info,
            address: this.address
          },
          {
            withCredentials: true
          }
        );

        if (response.status === 200 && response.data) {
          this.success = true;
        } else {
          console.error('Could not add business:', response);
          this.error = response.data.message || 'Could not add business. Server error.';
        }
      } catch (error) {
        console.error('Error adding business in:', error);
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
