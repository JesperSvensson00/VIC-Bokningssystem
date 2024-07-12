<template>
    <div v-if="submenu == 'createMeeting'" class="panel">
      <h2>Skapa nya mötestider</h2>
      <CreateMeetingView></CreateMeetingView>
    </div>
    <div v-else class="panel">
      <h2>Hantera möten</h2>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-else-if="filteredBookings.length == 0">Inga möten hittades</div>
      <div v-else>
        <div class="filter">
          <div>
            <label for="filterBookedInp">Visa enbart bokade</label>
            <input id="filterBookedInp" type="checkbox" v-model="filterBooked" />
            {{ filterBooked ? 'Ja' : 'Nej' }}
          </div>
        </div>
  
        <div class="booking">
          <div>Datum</div>
          <div>Starttid</div>
          <div>Sluttid</div>
          <div>Namn</div>
        </div>
        <div id="bookingsList" class="scroll">
          <div v-for="booking in filteredBookings" :key="booking.id" class="booking">
            <div>{{ booking.date }}</div>
            <div>{{ booking.start_time }}</div>
            <div>{{ booking.end_time }}</div>
            <div v-if="booking.name">{{ booking.name }}</div>
            <div v-else>Ej bokat</div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'; // Import axios for HTTP requests
  import CreateMeetingView from './CreateMeetingView.vue';
  
  export default {
    name: 'ManageUsersView',
    props: {
      submenu: String
    },
    components: {
      CreateMeetingView
    },
    data() {
      return {
        allBookings: [],
        filterBooked: false,
        error: '',
        success: false
      };
    },
    methods: {},
    computed: {
      filteredBookings() {
        if (this.filterBooked) {
          return this.allBookings.filter((booking) => booking.name);
        } else {
          return this.allBookings;
        }
      }
    },
    async created() {
      // Fetch data using Axios when the component is created
      const userID = this.$store.getters.getUserId;
      const response = await axios.get(SERVER_URL + '/api/user/' + userID + '/meetings', {
        withCredentials: true
      });
  
      if (response.status !== 200) {
        this.error = 'Kunde inte hämta användare';
        return;
      }
      console.log(response.data.meetings);
      // this.allBookings.push(...response.data.meetings);
      this.allBookings = response.data.meetings;
    }
  };
  </script>
  
  <style scoped>
  #bookingsList {
    height: 30rem;
    overflow-y: scroll;
  }
  
  .booking {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    gap: 1rem;
    background-color: var(--background);
    padding: 0.5rem;
    border: 2px solid var(--skyblue);
    border-radius: 0.5rem;
    margin: 0.5rem 1rem;
  }
  
  .filter {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    gap: 1rem;
  }
  
  .filter > div {
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
  }
  </style>
  