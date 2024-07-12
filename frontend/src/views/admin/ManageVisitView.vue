<template>
  <div v-if="submenu == 'createVisit'" class="panel">
    <h2>Skapa nytt studiebesök</h2>
    <CreateVisitView></CreateVisitView>
  </div>
  <div v-else-if="submenu == 'createGroup'" class="panel">
    <h2>Skapa ny grupp</h2>
    <CreateGroupView></CreateGroupView>
  </div>
  <div v-else-if="submenu == ''" class="panel">
    <h2>Hantera studiebesök</h2>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!selectedGroupId" class="list scroll">
      <h3>Välj kurs/grupp</h3>
      <ul>
        <li v-for="group in groups" :key="group.id">
          <div class="info">
            <p>{{ group.name }}</p>
          </div>
          <button class="small" @click="fetchVisits(group.id)">Visa mer</button>
          <button class="small remove" @click="removeGroup(group.id)">Ta bort</button>
        </li>
      </ul>
    </div>

    <div v-if="selectedGroupId" class="list scroll">
      <h3>Studiebesök för vald grupp</h3>
      <p v-if="visits.length == 0">Inga studiebesök tillagda i denna gruppen</p>
      <ul>
        <li v-for="visit in visits" v-bind:key="visit.id">
          <div class="info">
            <p>Titel: {{ visit.title }}</p>
            <p>Datum: {{ visit.date }}</p>
            <p>Tid: {{ visit.start_time }} - {{ visit.end_time }}</p>
          </div>
          <div class="options">
            <button class="small" @click="fetchVisitDetails(visit.id)">Besökare</button>
            <button class="small remove" @click="removeVisit(visit.id)">Ta bort</button>
          </div>
        </li>
      </ul>
      <button @click="resetVisits">Välj en annan grupp</button>
    </div>
  </div>
  <div v-else-if="submenu == 'visitDetails'" class="panel">
    <p v-if="booked">{{ booked }}</p>
    <h3>Studiebesök på {{ selectedVisit.business.name }}</h3>
    <div class="detailsContainer">
      <div class="details">
        <div class="head">
          <p>Titel</p>
          <p>Datum</p>
          <p>Tid</p>
          <p>Besökare</p>
        </div>
        <div class="info">
          <p>{{ selectedVisit.title }}</p>
          <p>{{ selectedVisit.date }}</p>
          <p>
            {{ selectedVisit.start_time.match(/^\d{2}:\d{2}/)[0] }} -
            {{ selectedVisit.end_time.match(/^\d{2}:\d{2}/)[0] }}
          </p>
          <p>{{ selectedVisit.attendees.length }} av {{ selectedVisit.spots }}</p>
        </div>
      </div>
      <h4 v-if="selectedVisit.attendees.length > 0">Besökare</h4>
      <h4 v-else>Inga besökare</h4>
      <div class="attendeesList scroll">
        <ul>
          <li v-for="attendee in selectedVisit.attendees" :key="attendee.id">
            <div>
              <p>{{ attendee.name }}</p>
              <p>{{ attendee.email }}</p>
            </div>
            <div class="options">
              <button @click="removeAttendee(attendee.id)">Avboka</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div class="options">
      <button @click="clearVisit">Tillbaka till lista</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CreateVisitView from './CreateVisitView.vue';
import CreateGroupView from './CreateGroupView.vue';

export default {
  props: {
    submenu: String
  },
  components: {
    CreateVisitView,
    CreateGroupView
  },
  data() {
    return {
      groups: [],
      visits: [],
      selectedGroupId: null,
      selectedVisit: null,
      error: ''
    };
  },
  methods: {
    async fetchVisits(groupId) {
      try {
        // Fetch visits associated with the selected group
        const response = await axios.get(`${SERVER_URL}/api/group/${groupId}/visits`, {
          withCredentials: true
        });
        // Store the fetched visits in the visits array
        this.visits = response.data.visits;
        console.log('data visits ', response.data.visits);
        // Set the selected group ID
        this.selectedGroupId = groupId;
      } catch (error) {
        console.error('Error fetching visits:', error);
      }
    },

    async removeGroup(groupId) {
      const response = await axios.delete(SERVER_URL + '/api/group/' + groupId, {
        withCredentials: true
      });

      if (response.status !== 200) {
        this.error = 'Kunde inte ta bort grupp';
        return;
      }

      this.groups = this.groups.filter((group) => group.id !== groupId);
    },
    resetVisits() {
      // Reset the selected group ID and visits array
      this.selectedGroupId = null;
      this.visits = [];
    },
    async fetchVisitDetails(visitId) {
      this.booked = '';
      const response = await axios.get(`${SERVER_URL}/api/visit/${visitId}`, {
        withCredentials: true
      });
      // Uppdatera selectedVisit med den hämtade studiebesöksinformationen
      this.selectedVisit = response.data.visit;
      console.log('data detaljer studiebesök ', response.data.visit);
      this.$emit('change-submenu', 'visitDetails');
    },
    clearVisit() {
      this.selectedVisit = null;
      this.$emit('change-submenu', '');
    },
    async removeAttendee(attendeeId) {
      const response = await axios.delete(
        `${SERVER_URL}/api/visit/${this.selectedVisit.id}/user/${attendeeId}`,
        {
          withCredentials: true
        }
      );

      if (response.status !== 200) {
        this.error = 'Kunde inte avboka besökaren';
        return;
      }

      this.selectedVisit.attendees = this.selectedVisit.attendees.filter(
        (attendee) => attendee.id !== attendeeId
      );
    }
  },

  async created() {
    // Fetch data using Axios when the component is created
    const response = await axios.get(SERVER_URL + '/api/groups', {
      withCredentials: true
    });
    // Store the fetched data in the groups array
    this.groups = response.data.groups;
    console.log('data groups ', response.data.groups);
  }
};
</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 90%;
  padding: 2rem 0;

  max-height: 20rem;
  overflow-y: auto;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

li {
  background-color: white;
  border: 2px solid var(--skyblue);
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

li > div {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
}

.visit {
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

.details {
  display: grid;
  grid-template-columns: repeat(4, auto);
  grid-template-rows: repeat(2, 1fr);
  align-items: center;
  grid-row-gap: 0.5rem;
  min-width: 30rem;
  max-width: 40rem;
  padding: 1rem 0;

  background-color: white;
  border: 2px solid var(--skyblue);
  border-radius: 0.5rem;
}

h4 {
  padding-top: 1rem;
  padding-bottom: 0.5rem;
  text-align: center;
}

.details > div {
  padding: 0 1rem;

  display: grid;
  column-gap: 0.5rem;
  grid-template-columns: subgrid;
}

.details > div > p:not(:first-child) {
  /* border-left: 1px var(--skyblue) dashed; */
  padding-left: 0.5rem;
}

.head {
  grid-area: 1 / 1 / 2 / 5;
}

.info {
  grid-area: 2 / 1 / 3 / 5;
}

.attendeesList {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 30rem;
  max-width: 40rem;
}

.attendeesList li {
  padding: 0.5rem 1rem;
  max-height: 30rem;
  overflow-y: auto;
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
