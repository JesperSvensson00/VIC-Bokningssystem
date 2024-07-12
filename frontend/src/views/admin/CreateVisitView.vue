<template>
  <div class="createVisitPanel">
    <div v-if="!success" class="inputs">
      <input
        id="title"
        :class="{ error: !validateTitle() }"
        type="text"
        placeholder="Titel"
        v-model="title"
      />
      <div class="inputRow">
        <label for="groupSel">Välj grupp som kan gå på besöket</label>
        <select id="groupSel" v-model="selectedGroup">
          <option v-bind:key="group.id" :value="group.id" v-for="group in groups">
            {{ group.name }}
          </option>
        </select>
      </div>

      <div class="inputRow">
        <label for="businessSel">Välj företag för besöket</label>
        <select id="businessSel" v-model="selectedBusiness">
          <option v-bind:key="business.id" :value="business.id" v-for="business in businesses">
            {{ business.name }}
          </option>
        </select>
      </div>

      <div class="inputRow">
        <label for="date">Datum</label>
        <input id="date" :class="{ error }" type="date" v-model="date" />
      </div>
      <div class="inputRow">
        <label for="start_time">Starttid för besöket</label>
        <input id="start_time" :class="{ error }" type="time" v-model="start_time" />
      </div>
      <div class="inputRow">
        <label for="end_time">Sluttid för besöket</label>
        <input id="end_time" :class="{ error }" type="time" v-model="end_time" />
      </div>
      <div class="inputRow">
        <label for="number_of_spots">Antal platser</label>
        <input
          id="number_of_spots"
          :class="{ error }"
          type="number_of_spots"
          v-model="number_of_spots"
        />
      </div>
      <button @click="createVisit(selectedGroup)">Skapa studiebesök</button>
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
      groups: [],
      group: [],
      selectedGroup: '',
      businesses: [],
      business: [],
      selectedBusiness: [],
      selfUser: {},
      title: '',
      date: '',
      start_time: '',
      end_time: '',
      number_of_spots: '',
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
    async createVisit(groupId) {
      try {
        this.error = ''; // Clear any previous error messages

        const response = await axios.post(
          `${SERVER_URL}/api/group/${groupId}/visit`,
          {
            visit_title: this.title,
            date: this.date,
            start_time: this.start_time,
            end_time: this.end_time,
            number_of_spots: this.number_of_spots,
            business_id: this.selectedBusiness
          },
          {
            withCredentials: true
          }
        );
        console.log('groupId: ', groupId);
        if (response.status === 200 && response.data) {
          this.success = true;
          console.log('Visit created:', response.data);
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
    const groupResponse = await axios.get(SERVER_URL + '/api/groups', {
      withCredentials: true
    });

    const businessResponse = await axios.get(SERVER_URL + '/api/businesses', {
      withCredentials: true
    });

    // Store the fetched data in the groups array
    this.groups = groupResponse.data.groups;
    this.businesses = businessResponse.data.businesses;
    console.log('businesses: ', businessResponse.data.businesses);
    console.log('goups: ', groupResponse.data.groups);
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
