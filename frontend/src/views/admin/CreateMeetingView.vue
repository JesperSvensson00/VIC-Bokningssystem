<template>
  <div class="createMeetingPanel">
    <div v-if="!success" class="inputs">
      <input
        id="title"
        :class="{ error: !validateTitle() }"
        type="text"
        placeholder="Titel"
        v-model="title"
      />
      <div class="inputRow">
        <label for="attendeeSel">Välj vem som ska gå på mötet</label>
        <select id="attendeeSel" v-model="selectedAttendee">
          <!-- <option disabled selected :value="selfUser.id">
            {{ selfUser.name }}
          </option> -->
          <option v-bind:key="attendee.id" :value="attendee.id" v-for="attendee in allAttendees">
            {{ attendee.name }}
          </option>
        </select>
      </div>
      <div class="inputRow">
        <label for="date">Datum</label>
        <input id="date" :class="{ error }" type="date" v-model="date" />
      </div>
      <div class="inputRow">
        <label for="start_time">Tid för första mötet</label>
        <input id="start_time" :class="{ error }" type="time" v-model="start_time" />
      </div>
      <div class="inputRow">
        <label for="end_time">Senaste möjlig sluttid för sista mötet</label>
        <input id="end_time" :class="{ error }" type="time" v-model="end_time" />
      </div>
      <div class="inputRow">
        <label for="length">Längd på varje möte (min)</label>
        <input id="length" :class="{ error }" type="number" v-model="length" />
      </div>
      <button @click="createMeeting">Skapa tider</button>
    </div>
    <div v-if="success">
      <p>Mötestider tillagda</p>
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
      allAttendees: [],
      selectedAttendee: '',
      title: '',
      date: '',
      start_time: '',
      end_time: '',
      length: '',
      error: '',
      success: false
    };
  },
  methods: {
    validateTitle() {
      if (this.title.length < 3 && this.title.length !== 0) {
        console.log('Title too short:', this.title);
        return false;
      } else {
        return true;
      }
    },
    async createMeeting() {
      try {
        this.error = ''; // Clear any previous error messages

        const response = await axios.post(
          SERVER_URL + `/api/meeting`,
          {
            title: this.title,
            date: this.date,
            start_time: this.start_time,
            end_time: this.end_time,
            length: this.length,
            attendee_id: this.selectedAttendee
          },
          {
            withCredentials: true
          }
        );

        if (response.status === 200 && response.data) {
          this.success = true;
          console.log('Meeting created:', response.data);
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
  async created() {
    this.selectedAttendee = this.$store.getters.getUser.id;
    try {
      const response = await axios.get(SERVER_URL + '/api/admins', {
        withCredentials: true
      });

      if (response.status === 200 && response.data) {
        this.allAttendees = response.data.admins;
        console.log('Attendees:', response.data);
      } else {
        console.error('Failed to get attendees:', response);
        this.error = response.data.message || 'Failed to get attendees. Server error.';
      }
    } catch (error) {
      console.error('Error getting attendees:', error);
      if (error.response && error.response.data) {
        this.error = error.response.data.detail || 'An error occurred. Please try again.';
      } else {
        this.error = 'An error occurred. Please try again.';
      }
    }
  }
};
</script>

<style scoped>
.createMeetingPanel {
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

.inputRow {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

option {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
