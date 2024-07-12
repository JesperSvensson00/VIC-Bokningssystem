<template>
  <div class="createGroupPanel">
    <div v-if="!success" class="inputs">
      <input
        id="name"
        type="text"
        placeholder="Gruppnamn"
        v-model="name"
        @blur="validateName"
      />
      <input
        id="max_visit"
        type="number"
        placeholder="Maxantal bokningar"
        v-model="max_visit"
        @blur="validateNumber"
      />
      <button @click="createGroup">Skapa grupp</button>
    </div>
    <div v-if="success">
      <p>Gruppen är skapad</p>

    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests

export default {
  data() {
    return {
      selfUser: {},
      name: '',
      max_visit: '',
      success: false,
      error: ''
    };
  },
  methods: {
    validateName() {
      if (this.name.length < 3 && this.name.length !== 0) {
        console.log('Title too short:', this.title);
        return false;
      } else {
        return true;
      }
    },
    validateNumber() {
        if (this.max_visit.length < 1 && this.max_visit.length !== 0){
          console.log('för kort input', this.max_visit);
          return false;
        } else{ return true;}
    },
   
    async createGroup() {
      try {
        this.error = ''; // Clear any previous error messages

        // Validate name
        if (!this.validateName()) {
          this.error = 'Namnet måste vara minst 2 tecken.';
          console.error('Invalid name:', this.name);
          return; // Don't proceed with login if name is invalid
        }
        if (!this.validateNumber()){
          this.error = 'Ett antal måste angivas. ';
          return;
        }

        const response = await axios.post(
          SERVER_URL + `/api/group`,
          {
            name: this.name,
            max_visit: this.max_visit
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
  },
  
};
</script>

<style scoped>
.createGroupPanel {
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
