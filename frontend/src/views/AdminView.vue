<script setup></script>

<template>
  <main>
    <header>
      <h1>Adminportal</h1>
      <h2>Hej {{ name }}</h2>
    </header>
    <div>
      <div class="menu">
        <!-- Huvudmeny -->
        <div v-if="showView == ''" :class="showView == '' ? 'mainMenu' : ''">
          <button @click="showView = 'manageUsers'">Hantera användare</button>
          <button @click="showView = 'manageMeetings'">Hantera möten</button>
          <button @click="showView = 'manageVisits'">Hantera studiebesök</button>
          <button @click="showView = 'manageBusinesses'">Hantera företag</button>
        </div>

        <!-- Sub-meny för användare -->
        <div v-else-if="showView == 'manageUsers'">
          <button @click="submenu = 'createUser'" :class="{ selected: submenu === 'createUser' }">
            Skapa användare
          </button>
        </div>

        <!-- Sub-meny för möten -->
        <div v-else-if="showView == 'manageMeetings'">
          <button
            @click="submenu = 'createMeeting'"
            :class="{ selected: submenu === 'createMeeting' }"
          >
            Skapa nytt möte
          </button>
        </div>

        <!-- Sub-meny för studiebesök -->
        <div v-else-if="showView == 'manageVisits'">
          <button @click="submenu = 'createVisit'" :class="{ selected: submenu === 'createVisit' }">
            Skapa nya studiebesök
          </button>

          <button @click="submenu = 'createGroup'" :class="{ selected: submenu === 'createGroup' }">
            Skapa ny grupp
          </button>
        </div>

        <!-- Sub-meny för företag -->
        <div v-else-if="showView == 'manageBusinesses'">
          <button
            @click="submenu = 'createBusiness'"
            :class="{ selected: submenu === 'createBusiness' }"
          >
            Lägg till företag
          </button>
        </div>

        <!-- Tillbaka-knapp -->
        <div v-if="showView != ''">
          <button @click="menuBack()">Tillbaka</button>
        </div>
      </div>

      <!-- Panel för att visa innehåll -->
      <div class="panelWrapper">
        <ManageUsersView v-if="showView == 'manageUsers'" :submenu="submenu"></ManageUsersView>
        <ManageMeetingView
          v-else-if="showView == 'manageMeetings'"
          :submenu="submenu"
        ></ManageMeetingView>
        <ManageVisitView
          v-else-if="showView == 'manageVisits'"
          :submenu="submenu"
          @change-submenu="
            (m) => {
              submenu = m;
            }
          "
        ></ManageVisitView>
        <ManageBusinessesView
          v-else-if="showView == 'manageBusinesses'"
          :submenu="submenu"
        ></ManageBusinessesView>
      </div>
    </div>
  </main>
</template>

<script>
import ManageUsersView from './admin/ManageUsersView.vue';
import ManageMeetingView from './admin/ManageMeetingView.vue';
import ManageVisitView from './admin/ManageVisitView.vue';
import ManageBusinessesView from './admin/ManageBusinessesView.vue';

export default {
  components: {
    ManageUsersView,
    ManageMeetingView,
    ManageVisitView,
    ManageBusinessesView
  },
  computed: {
    name() {
      return this.$store.getters.getName;
    }
  },
  data() {
    return {
      showView: '',
      submenu: ''
    };
  },
  methods: {
    menuBack() {
      if (this.submenu != '') {
        this.submenu = '';
      } else {
        this.showView = '';
      }
    }
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

.mainMenu {
  justify-content: space-between;
  width: 100%;
}
</style>
