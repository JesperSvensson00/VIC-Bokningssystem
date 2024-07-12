<template>
  <main>
    <header>
      <h1>Boka möte</h1>
    </header>
    <p v-if="error" class="error-message">{{ error }}</p>
    <div v-if="submenu == ''">
      <h3>Välj vem du vill boka möte hos:</h3>
      <select v-model="creator_email" @change="fetchAvailableMeetings">
        <option v-for="admin in availableAdmins" v-bind:key="admin.email" :value="admin.email">
          {{ admin.name }} - {{ admin.email }}
        </option>
      </select>
    </div>

    <div v-else-if="submenu == 'meetingList'">
      <ul>
        <li
          @click="fetchMeetingDetails(meeting.id)"
          v-for="meeting in meetings"
          :key="meeting.id"
          class="meeting-item"
        >
          <p>Titel: {{ meeting.title }}</p>
          <p>Datum: {{ meeting.date }}</p>
          <p>Tid: {{ meeting.start_time }} - {{ meeting.end_time }}</p>
        </li>
      </ul>
    </div>

    <div v-else-if="submenu == 'meetingDetails'">
      <p v-if="booked" class="booked-message">{{ booked }}</p>
      <div v-else>
        <h3>Detaljer för valt möte</h3>
        <div class="details-container">
          <p>Titel: {{ selectedMeeting.title }}</p>
          <p>Datum: {{ selectedMeeting.date }}</p>
          <p>Tid: {{ selectedMeeting.start_time }} - {{ selectedMeeting.end_time }}</p>
        </div>
        <div class="message-item">
          <label for="bookingMessage">Meddelande: </label>
          <input
            v-model="bookingMessage"
            id="bookingMessage"
            type="text"
            placeholder="Ange meddelande"
          />
        </div>
      </div>
      <div class="button-center">
        <button v-if="!booked" class="book-button" @click="bookMeeting(selectedMeeting.id)">
          Boka möte
        </button>
        <button @click="clearMeeting">Tillbaka till lista</button>
      </div>
    </div>
  </main>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    submenu: String
  },
  data() {
    return {
      creator_email: '',
      meetings: [],
      availableAdmins: [],
      selectedMeeting: null,
      error: '',
      booked: '',
      bookingMessage: ''
    };
  },
  computed: {
    bookings() {
      if (this.yourbookings) {
        return this.allBookings.filter((booking) => booking.name);
      } else {
        return this.allBookings;
      }
    },
    userID() {
      return this.$store.getters.getUserId;
    }
  },
  methods: {
    async fetchAvailableAdmins() {
      try {
        const response = await axios.get(`${SERVER_URL}/api/admins/available`, {
          withCredentials: true
        });
        this.availableAdmins = response.data.admins;
        console.log('hejssss', this.availableAdmins);
      } catch (error) {
        console.error('Error fetching available admins:', error);
      }
    },
    async fetchAvailableMeetings() {
      // Fetch data using Axios with the user's email address
      try {
        const response = await axios.get(
          `${SERVER_URL}/api/available-meetings/${this.creator_email}`,
          {
            withCredentials: true
          }
        );
        this.meetings = response.data.meetings;
        console.log('data möten ', response.data.meetings);
        this.$emit('change-submenu', 'meetingList');
      } catch (error) {
        console.error('Error fetching meetings:', error);
      }
    },
    async fetchMeetingDetails(meetingId) {
      this.booked = '';
      this.error = '';
      const response = await axios.get(`${SERVER_URL}/api/meeting/${meetingId}`, {
        withCredentials: true
      });
      // Uppdatera selectedMeeting med den hämtade mötesinformationen
      this.selectedMeeting = response.data.meeting_data;
      console.log('data detaljer ', response.data.meeting_data);
      this.$emit('change-submenu', 'meetingDetails');
    },

    clearMeeting() {
      this.error = '';
      this.selectedMeeting = null;
      this.$emit('change-submenu', 'meetingList');
    },
    async bookMeeting(meetingId) {
      console.log('USERIDDDD: ', this.userID);
      try {
        await axios.post(
          `${SERVER_URL}/api/meeting/${meetingId}/user/${this.userID}`,
          {
            message: this.bookingMessage
          },
          {
            withCredentials: true
          }
        );
        console.log('bokad!');
        this.booked = 'Mötet är bokat!';
      } catch (error) {
        console.error('Error booking meeting:', error);
        if (error.response?.data) {
          console.log('error här', error.response?.data);
          this.error = error.response?.data.detail;
        }
      }
    }
  },

  mounted: function () {
    this.fetchAvailableAdmins();
    if (this.$route.params.id) {
      this.creator_email = this.$route.params.id;
      this.fetchAvailableMeetings();
    }
  }
};
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.container {
  border: 2px solid var(--skyblue);
  border-radius: 5px;
  background-color: var(--sand);
}

li {
  background-color: var(--sand);
  padding: 1rem;
  margin: 1rem;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.message-item {
  background-color: var(--sand);
  /* border: 2px solid var(--skyblue); */
  padding: 1rem;
  margin: 1rem;
  /* box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1); */
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.meeting-item {
  background-color: var(--sand);
  border: 2px solid var(--skyblue);
  padding: 1rem;
  margin: 1rem;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.meeting-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 1rem rgba(0, 0, 0, 0.2);
}

.details-container {
  background-color: white;
  border: 2px solid var(--skyblue);
  border-radius: 5px;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 0 1rem rgba(0, 0, 0, 0.1);
}

.booked-message {
  font-size: 1.5rem;
  color: green;
  background-color: lightyellow;
  padding: 1rem;
  margin: 1rem 0;
  text-align: center;
  border: 2px solid green;
  border-radius: 5px;
}

.error-message {
  font-size: 1.2rem;
  color: white;
  background-color: #9e4444;
  padding: 1rem;
  margin: 1rem 0;
  text-align: center;
  border: #9e4444;
  border-radius: 5px;
}

.details-container p {
  margin: 0.5rem 0;
}

.details-container strong {
  color: var(--kthblue);
}

.button-center {
  display: flex;
  justify-content: center;
  margin-top: 1rem; /* Add some spacing between buttons */
}

.book-button {
  margin-right: 1rem;
}
</style>
