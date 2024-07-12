<template>
  <main>
    <header>
      <h1>Boka studiebesök</h1>
    </header>
    <p v-if="error" class="error-message">{{ error }}</p>
    <div v-if="submenu == ''">
      <h3>Välj kurs/grupp</h3>
      <ul class="group-list"></ul>
      <ul>
        <li
          v-for="group in groups"
          :key="group.id"
          @click="fetchVisits(group.id)"
          class="group-item"
        >
          <p>{{ group.name }}</p>
        </li>
      </ul>
    </div>

    <div v-else-if="submenu == 'visitList'">
      <h3>Studiebesök för vald grupp</h3>
      <div class="panelWrapper">
        <ul>
          <li
            v-for="visit in visits"
            :key="visit.id"
            @click="fetchVisitDetails(visit.id)"
            class="visit-item"
          >
            <p>Titel: {{ visit.title }}</p>
            <p>Datum: {{ visit.date }}</p>
            <p>Tid: {{ visit.start_time }} - {{ visit.end_time }}</p>
          </li>
        </ul>
      </div>
      <button @click="resetVisits">Välj en annan grupp</button>
    </div>

    <div v-else-if="submenu == 'visitDetails'">
      <p v-if="booked" class="booked-message">{{ booked }}</p>
      <div v-else>
        <h3>Detaljer för valt studiebesök</h3>
        <div class="details-container">
          <p>Titel: {{ selectedVisit.title }}</p>
          <p>Datum: {{ selectedVisit.date }}</p>
          <p>Tid: {{ selectedVisit.start_time }} - {{ selectedVisit.end_time }}</p>
        </div>

        <div class="button-center">
          <button v-if="!booked" class="booking-button" @click="bookVisit(selectedVisit.id)">
            Boka studiebesök
          </button>
          <button @click="clearVisit">Tillbaka till lista</button>
        </div>
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
      groups: [],
      visits: [],
      selectedGroupId: null,
      selectedVisit: null,
      error: '',
      booked: ''
    };
  },
  computed: {
    userID() {
      return this.$store.getters.getUserId;
    }
  },
  methods: {
    async fetchVisits(groupId) {
      try {
        const response = await axios.get(`${SERVER_URL}/api/group/${groupId}/visits`, {
          withCredentials: true
        });
        this.visits = response.data.visits;
        this.selectedGroupId = groupId;
        this.$emit('change-submenu', 'visitList');
      } catch (error) {
        console.error('Error fetching visits:', error);
      }
    },
    async fetchVisitDetails(visitId) {
      this.booked = '';
      this.error = '';
      const response = await axios.get(`${SERVER_URL}/api/visit/${visitId}`, {
        withCredentials: true
      });
      this.selectedVisit = response.data.visit;
      this.$emit('change-submenu', 'visitDetails');
    },
    resetVisits() {
      this.error = '';
      this.selectedGroupId = null;
      this.visits = [];
      this.$emit('change-submenu', '');
    },
    clearVisit() {
      this.error = '';
      this.selectedVisit = null;
      this.booked = '';
      this.$emit('change-submenu', 'visitList');
    },
    async bookVisit(visitId) {
      try {
        await axios.post(
          `${SERVER_URL}/api/visit/${visitId}/user/${this.userID}`,
          { message: '' },
          { withCredentials: true }
        );
        this.booked = 'Studiebesöket är bokat!';
      } catch (error) {
        console.error('Error booking visit:', error);
        if (error.response?.data) {
          this.error = error.response?.data.detail;
        }
      }
    }
  },
  async created() {
    const response = await axios.get(SERVER_URL + '/api/groups', {
      withCredentials: true
    });
    this.groups = response.data.groups;
  }
};
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.panelWrapper {
  min-width: 30rem;
  border-radius: 0 0 5px 5px;
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

.group-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.group-item {
  background-color: var(--sand);
  padding: 1rem;
  margin: 1rem;
  border: 2px solid var(--kthblue);
  border-radius: 5px;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.group-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 1rem rgba(0, 0, 0, 0.2);
}

.visit-item {
  background-color: white;
  border: 2px solid var(--skyblue);
  padding: 1rem;
  margin: 1rem;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.visit-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 1rem rgba(0, 0, 0, 0.2);
}

.details-container {
  border: 2px solid var(--skyblue);
  border-radius: 5px;
  background-color: white;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 0 1rem rgba(0, 0, 0, 0.1);
}

.details-container p {
  margin: 0.5rem 0;
}

.details-container strong {
  color: var(--kthblue);
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

.booking-button {
  margin-right: 1rem;
}
.button-center {
  display: flex;
  justify-content: center;
  margin-top: 1rem; /* Add some spacing between buttons */
}
</style>
