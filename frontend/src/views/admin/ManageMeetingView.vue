<template>
  <div v-if="submenu == 'createMeeting'" class="panel">
    <h2>Skapa nya mötestider</h2>
    <CreateMeetingView></CreateMeetingView>
  </div>
  <div v-else class="panel">
    <h2>Hantera möten</h2>
    <div class="filter">
      <div>
        <label for="filterBookedInp">Visa enbart bokade</label>
        <input id="filterBookedInp" type="checkbox" v-model="filterBooked" />
      </div>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-else-if="filteredBookings.length == 0">Inga möten hittades</div>
    <div v-else>
      <div class="booking head">
        <div>Datum</div>
        <div>Starttid</div>
        <div>Sluttid</div>
        <div>Namn</div>
        <div>Meddelande</div>
      </div>
      <div id="bookingsList" class="scroll">
        <div v-for="booking in filteredBookings" :key="booking.id" class="booking">
          <div>{{ booking.date }}</div>
          <div>{{ booking.start_time.substring(0, 5) }}</div>
          <div>{{ booking.end_time.substring(0, 5) }}</div>
          <div v-if="booking.booked_by?.name">{{ booking.booked_by?.name }}</div>
          <div v-else>Ej bokat</div>
          <div>{{ booking.booked_by?.message || '' }}</div>
          <div class="options">
            <button v-if="booking.booked_by?.name" class="small" @click="kickAttendee(booking.id)">
              Avboka
            </button>
            <button class="small remove" @click="removeMeeting(booking.id)">Ta bort</button>
          </div>
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
  methods: {
    async kickAttendee(id) {
      console.log('Kick attendee');
      try {
        const booking = this.allBookings.find((booking) => booking.id === id);

        const response = await axios.delete(
          SERVER_URL + `/api/meeting/${id}/user/${booking.booked_by.id}`,
          {
            withCredentials: true
          }
        );

        if (response.status !== 200) {
          this.error = 'Kunde inte avboka möte';
          return;
        }

        // Tar bort namn från mötet
        booking.booked_by = {};

        // Uppdaterar lokal lista
        this.allBookings = [...this.allBookings];
      } catch (error) {
        console.error('Error kicking attendee:', error);
      }
    },
    async removeMeeting(id) {
      console.log('Remove meeting');
      try {
        const response = await axios.delete(SERVER_URL + '/api/meeting/' + id, {
          withCredentials: true
        });
        if (response.status !== 200) {
          this.error = 'Kunde inte ta bort möte';
          return;
        }

        // Tar bort från lokal lista
        this.allBookings = this.allBookings.filter((booking) => booking.id !== id);
      } catch (error) {
        console.error('Error removing meeting:', error);
      }
    }
  },
  computed: {
    filteredBookings() {
      if (this.filterBooked) {
        return this.allBookings.filter((booking) => {
          console.log(booking.booked_by);
          return booking.booked_by?.id ? true : false;
        });
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
  padding: 0 1rem;
  max-height: 20rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  margin-top: 1rem;
  gap: 0.6rem;
}

.booking {
  display: grid;
  grid-template-columns: 7rem 4rem 4rem 1.2fr 2fr auto;
  gap: 1rem;
  background-color: var(--background);
  padding: 0.5rem;
  align-items: center;
  border: 2px solid var(--skyblue);
  border-radius: 0.5rem;
}

.head {
  margin: 0 1rem 0 1rem;
}

.filter {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.5rem;
}

.filter > div {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.options {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 1rem;
}

button {
  font-size: 0.8rem;
  padding: 0.5rem;
  border: none;
  border-radius: 0.5rem;
  background-color: var(--skyblue);
  color: var(--background);
  cursor: pointer;
}

button:hover {
  background-color: var(--kthblue);
}
</style>
