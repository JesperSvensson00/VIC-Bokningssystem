<template>
  <main>
    <h1>Vi som skapat VICan Bokningssystem</h1>
    <div class="list">
      <div>
        <p>Matilda Algotsson</p>
        <div class="contact">
          <a href="mailto:matalg@kth.se">Mail</a>
          <a href="https://www.linkedin.com/in/matilda-algotsson/">LinkedIn</a>
        </div>
      </div>
      <div>
        <p>Ludwig Gustafsson</p>
        <div class="contact">
          <a href="mailto:ludwiggu@kth.se">Mail</a>
          <a href="https://www.linkedin.com/in/ludwiggustafsson/">LinkedIn</a>
        </div>
      </div>
      <div>
        <p>Gabriella Hajto</p>
        <div class="contact">
          <a href="mailto:hajto@kth.se">Mail</a>
          <!-- <a href="https://www.linkedin.com/in/">LinkedIn</a> -->
        </div>
      </div>
      <div>
        <p>Felicia Linder</p>
        <div class="contact">
          <a href="mailto:felinde@kth.se">Mail</a>
          <!-- <a href="https://www.linkedin.com/in/">LinkedIn</a> -->
        </div>
      </div>
      <div>
        <p>Jesper Svensson</p>
        <div class="contact">
          <a href="mailto:jesps@kth.se">Mail</a>
          <a href="https://www.linkedin.com/in/jespersvensson00/">LinkedIn</a>
        </div>
      </div>
      <div>
        <p>Hanna Westerdahl</p>
        <div class="contact">
          <a href="mailto:hwesterd@kth.se">Mail</a>
          <!-- <a href="https://www.linkedin.com/in/">LinkedIn</a> -->
        </div>
      </div>
      <div>
        <p>Moa Wettby</p>
        <div class="contact">
          <a href="mailto:mwettby@kth.se">Mail</a>
          <a href="https://www.linkedin.com/in/moa-wettby-750760257/">LinkedIn</a>
        </div>
      </div>
    </div>

    <div id="about">
      <h2>Om projektet</h2>
      <p>Bokningssystemet skapades som en del i kursen DD1367.</p>
    </div>
  </main>
</template>

<style scoped>
.list {
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  /* align-items: stretch; */
  align-items: center;
  gap: 0.5rem;
}

.list > div {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 1rem;
}

.contact {
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

a {
  color: var(--kthblue);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

p {
  font-size: 1.2rem;
}

h1 {
  padding-top: 10rem;
  color: var(--kthblue);
}

#about {
  padding-top: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style>
