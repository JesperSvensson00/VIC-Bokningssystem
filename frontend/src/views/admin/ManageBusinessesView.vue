<template>
  <div v-if="submenu == 'createBusiness'" class="panel">
    <h2>Lägg till nytt företag</h2>
    <CreateBusinessView></CreateBusinessView>
  </div>
  <div v-else class="panel">
    <h2>Hantera företag</h2>
    <div v-if="error" class="error">{{ error }}</div>

    <div id="list" class="scroll">
      <ul>
        <li v-for="business in businesses" :key="business.id">
          <div class="info">
            <p>Namn: {{ business.name }}</p>
            <p>Info: {{ business.info }}</p>
            <p>Adress: {{ business.address }}</p>
          </div>
          <button class="small remove" @click="removeBusiness(business.id)">Ta bort</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CreateBusinessView from './CreateBusinessView.vue';

export default {
  props: {
    submenu: String
  },
  components: {
    CreateBusinessView
  },
  data() {
    return {
      businesses: [],
      error: ''
    };
  },
  methods: {
    async removeBusiness(businessId) {
      const response = await axios.delete(SERVER_URL + '/api/business/' + businessId, {
        withCredentials: true
      });

      if (response.status !== 200) {
        this.error = 'Kunde inte ta bort företag';
        return;
      }

      this.businesses = this.businesses.filter((business) => business.id !== businessId);
    }
  },
  async created() {
    try {
      // Fetch visits associated with the selected group
      const response = await axios.get(`${SERVER_URL}/api/businesses`, {
        withCredentials: true
      });
      // Store the fetched visits in the visits array
      this.businesses = response.data.businesses;
      console.log('data businesses ', response.data.businesses);
    } catch (error) {
      console.error('Error fetching businesses:', error);
    }
  }
};
</script>

<style scoped>
#list {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 90%;

  max-height: 30rem;
  overflow-y: scroll;
}

.options {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 1rem;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
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

.panelWrapper {
  min-width: 30rem;
  border: 5px solid var(--kthblue);
  border-radius: 0 0 5px 5px;
  background-color: var(--sand);
}

li {
  background-color: white;
  padding: 1rem;
  margin: 1rem;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-radius: 0.4rem;
  border: 2px solid var(--skyblue);
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

.info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: start;
  align-items: start;
}
</style>
