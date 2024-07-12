<script setup></script>

<template>
  <main>
    <header>
      <h1>Studentportal</h1>
      <h2>Inloggad som {{ name }}</h2>
    </header>
    <div>
      <div class="menu">
        <!-- Huvudmeny -->
        <div v-if="showView == ''">
          <button @click="showView = 'manageMeeting'">Boka nytt möte</button>
          <button @click="showView = 'manageVisit'">Boka nytt studiebesök</button>
          <button @click="showView = 'manageAccount'">Radera konto</button>
        </div>

        <!-- Sub-meny för möten -->
        <div v-else-if="showView == 'manageMeeting'">
          <button class="selected">Boka Möte</button>
        </div>

        <!-- Sub-meny för studiebesök -->
        <div v-else-if="showView == 'manageVisit'">
          <button class="selected">Boka Studiebesök</button>
        </div>

        <!-- Sub-meny för studiebesök -->
        <div v-else-if="showView == 'manageAccount'">
          <button
            @click="submenu = 'deleteAccount'"
            :class="{ selected: submenu === 'deleteAccount' }"
          >
            Radera
          </button>
        </div>

        <!-- Tillbaka-knapp -->
        <div>
          <button v-if="showView != ''" @click="menuBack()">Tillbaka</button>
        </div>
      </div>

      <!-- Panel för att visa innehåll -->
      <div class="panelWrapper">
        <BookMeetingView
          v-if="showView == 'manageMeeting'"
          :submenu="submenu"
          @change-submenu="
            (m) => {
              submenu = m;
            }
          "
        ></BookMeetingView>
        <BookVisitView
          v-else-if="showView == 'manageVisit'"
          :submenu="submenu"
          @change-submenu="
            (m) => {
              submenu = m;
            }
          "
        ></BookVisitView>
        <div v-else class="panel">
          <h2>Här är dina bokade möten</h2>
          <ul>
            <!-- Lägg till kod för att visa alla inbokade studiebesök -->
            <div v-for="booking in bookings" :key="booking.id" class="booking">
              <div><span class="date">Datum:</span> {{ booking.date }}</div>
              <div>
                <span class="date">Tid:</span> {{ booking.start_time }} - {{ booking.end_time }}
              </div>
              <div><span class="date">Med:</span> {{ booking.booked_by.name }}</div>
              <div>
                <button class="remove" @click="removeBooking(booking.id)">Avboka</button>
              </div>
            </div>
          </ul>

          <h2>Här är dina bokade studiebesök</h2>
          <div>
            <ul>
              <!-- Lägg till kod för att visa alla inbokade studiebesök -->
              <div v-for="visit in visits" :key="visit.id" class="booking">
                <div><span class="date">Titel:</span> {{ visit.title }}</div>
                <div><span class="date">Datum:</span> {{ visit.date }}</div>
                <div>
                  <span class="date">Tid:</span> {{ visit.start_time }} - {{ visit.end_time }}
                </div>
                <div><span class="date">Företag:</span> {{ visit.business_name }}</div>
                <div><span class="date">Grupp:</span> {{ visit.group_name }}</div>
                <div>
                  <button class="remove" @click="removeVisit(visit.id)">Avboka</button>
                </div>
              </div>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import axios from 'axios'; // Import axios for HTTP requests
import BookMeetingView from './student/BookMeetingView.vue';
import BookVisitView from './student/BookVisitView.vue';

export default {
  components: {
    BookMeetingView,
    BookVisitView
  },
  props: {
    startSubmenu: String,
    startView: String
  },
  data() {
    return {
      showView: '',
      submenu: '',
      yourbookings: false,
      yourvisits: false,
      allBookings: [],
      allVisits: []
    };
  },

  methods: {
    menuBack() {
      if (this.submenu != '') {
        this.submenu = '';
      } else {
        this.showView = '';
      }
    },
    async removeBooking(bookingId) {
      try {
        // Send a DELETE request to remove the booking
        await axios.delete(
          `${SERVER_URL}/api/meeting/${bookingId}/user/${this.$store.getters.getUserId}`,
          {
            withCredentials: true
          }
        );
        // Update the list of bookings after removal
        this.allBookings = this.allBookings.filter((booking) => booking.id !== bookingId);
      } catch (error) {
        console.error('Error removing booking:', error);
      }
    },
    // Method to remove a visit
    async removeVisit(visitId) {
      try {
        // Send a DELETE request to remove the visit
        await axios.delete(
          `${SERVER_URL}/api/visit/${visitId}/user/${this.$store.getters.getUserId}`,
          {
            withCredentials: true
          }
        );
        // Update the list of visits after removal
        this.allVisits = this.allVisits.filter((visit) => visit.id !== visitId);
      } catch (error) {
        console.error('Error removing visit:', error);
      }
    }
  },

  computed: {
    name() {
      return this.$store.getters.getName;
    },
    bookings() {
      if (this.yourbookings) {
        return this.allBookings.filter((booking) => booking.name);
      } else {
        return this.allBookings;
      }
    },
    visits() {
      if (this.yourvisits) {
        return this.allVisits.filter((visit) => visit.name);
      } else {
        return this.allVisits;
      }
    }
  },
  async created() {
    // Sätter showView till startView och submenu till startSubmenu
    this.showView = this.startView || '';
    this.submenu = this.startSubmenu || '';

    // Fetch data using Axios when the component is created
    const userID = this.$store.getters.getUserId;
    const response = await axios.get(SERVER_URL + '/api/user/' + userID + '/meetings', {
      withCredentials: true
    });
    const response2 = await axios.get(SERVER_URL + '/api/user/' + userID + '/visits', {
      withCredentials: true
    });

    if (response.status !== 200) {
      this.error = 'Kunde inte hämta användare';
      return;
    }
    console.log('data meetings ', response.data.meetings);
    console.log('data ', response.data);
    console.log('data visits ', response2.data.visits);
    // this.allBookings.push(...response.data.meetings);
    this.allBookings = response.data.meetings;
    this.allVisits = response2.data.visits;
  }
};
</script>

<style scoped>
.menu {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 1rem;
  min-width: 50rem;
}

.menu button {
  border-radius: 5px 5px 0 0;
}

.menu div {
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.date {
  font-weight: 900;
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

.panelWrapper {
  min-width: 30rem;
  border: 5px solid var(--kthblue);
  border-radius: 0 0 5px 5px;
  background-color: var(--sand);
}

/* För alla sub-menyer */
.panel {
  margin: 2rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

/* Center-align the h3 element */
.panel h2 {
  text-align: center;
  margin-top: 0;
}

/* Deep för att child components ska få stylen */
.panel:deep(.subPanel) {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.selected {
  background-color: var(--skyblue);
  color: var(--sand);
}
</style>
