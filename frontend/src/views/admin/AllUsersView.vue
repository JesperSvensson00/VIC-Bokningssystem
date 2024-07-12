<template>
  <div class="subPanel" id="allUsersPanel">
    <input
      type="text"
      placeholder="Sök efter namn, e-post eller id"
      v-model="query"
      @input="search"
    />
    <div id="usersList" class="scroll">
      <div v-for="user in filteredUsers" :key="user.id" class="user">
        <div class="info">
          <p>{{ user.name }}</p>
          <p>{{ user.email }}</p>
          <p>{{ user.admin ? 'Admin' : 'Användare' }}</p>
        </div>
        <div class="options">
          <button @click="toggleAdmin(user)">
            {{ user.admin ? 'Ta bort admin-behörighet' : 'Gör till admin' }}
          </button>
          <button class="small remove" @click="removeUser(user)">Ta bort</button>
        </div>
      </div>
      <div class="error" v-if="!filteredUsers.length">
        <p>Inga användare kunde hittas!</p>
      </div>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup></script>

<script>
import axios from 'axios'; // Import axios for HTTP requests

export default {
  data() {
    return {
      query: '',
      filteredUsers: [],
      users: [],
      error: '',
      success: false
    };
  },
  async created() {
    // Fetch data using Axios when the component is created
    const response = await axios.get(SERVER_URL + '/api/users', {
      withCredentials: true
    });

    if (response.status !== 200) {
      this.error = 'Kunde inte hämta användare';
      return;
    }

    console.log(response.data.users);
    // Store the fetched data in the dataList array
    this.users = response.data.users;
    this.filteredUsers = this.users;
  },
  methods: {
    async removeUser(user) {
      const response = await axios.delete(SERVER_URL + '/api/user/' + user.id, {
        withCredentials: true
      });

      if (response.status !== 200) {
        this.error = 'Kunde inte ta bort användare';
        return;
      }

      this.filteredUsers = this.filteredUsers.filter((u) => u.id !== user.id);
    },
    async toggleAdmin(user) {
      console.log(this.$store.getters.getUserId);
      const response = await axios.put(
        SERVER_URL + '/api/user/' + user.id,
        {
          admin: !user.admin
        },
        {
          withCredentials: true
        }
      );

      if (response.status !== 200) {
        this.error = 'Kunde inte ändra användarens roll';
        return;
      }

      this.users = this.users.map((existingUser) => {
        if (existingUser.id === user.id) {
          existingUser.admin = response.data.user[3];
        }
        return existingUser;
      });
    },
    search() {
      this.filteredUsers = this.users.filter((user) => {
        return (
          user.name.toLowerCase().includes(this.query.toLowerCase()) ||
          user.email.toLowerCase().includes(this.query.toLowerCase()) ||
          user.id.toString().includes(this.query)
        );
      });
    }
  }
};
</script>

<style scoped>
#usersList {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 90%;
  padding: 2rem 0;

  max-height: 20rem;
  overflow-y: scroll;
}

.user {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem;
  border: 1px solid var(--skyblue);
  border-radius: 0.5rem;
  min-width: 40rem;
  background-color: var(--background);
  box-shadow: 0 0 8px 2px rgba(0, 0, 0, 0.1);
}

.user .info {
  display: flex;
  flex-direction: row;
  align-items: center;
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

input {
  width: 50%;
}
</style>
