const exempelUser = {};

async function findMeetings() {
  const gruppId = document.getElementById("idInp").value;

  console.log("Hej", gruppId);
  return;
  let res = await fetch("/group", {
    //försöker komma åt login från databasen
    method: "GET",
    body: {
      email: "test" //skickar med emai
    }
  });
}

async function adminLogin() {
  const email = document.getElementById("emailInput").value;
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email })
  };
  let res = await fetch("/login", options);
  let body = await res.json();

  if (res.status === 404) {
    alert("Användaren finns inte");
    return;
  }

  if (res.status !== 200) {
    alert("Något gick fel");
    return;
  }

  const greetingElem = document.getElementById("greeting");
  greetingElem.innerHTML = `Välkommen ${body.name}!`;

  document.getElementById("loginPanel").hidden = true;
  document.getElementById("menuPanel").hidden = false;
  console.log(document.getElementById("loginPanel"))


}

async function addUser(){
  const email = document.getElementById("newUserEmail").value;
  const name = document.getElementById("newUserName").value;
  const admin = document.getElementById("newUserAdmin").checked;

  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, name, admin })
  };

  let res = await fetch("/user", options);
  let body = await res.json();

  if (res.status === 401) {
    alert("Användaren finns inte");
    return;
  }

  console.log(body);


}

async function adminGetGroups() {
  let res = await fetch("/groups");
  let body = await res.json();

  console.log(body);

  for (let group of body.groups) {
    const groupElem = document.createElement("div");
    let deleteButton = document.createElement("button");
    deleteButton.innerHTML = "Delete";

    deleteButton.onclick = async () => {
      let res = await fetch("/group/"+ group[0], {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json"
        },
      });
      let body = await res.json();
      console.log(body);

      if (res.status !== 200) {
        alert("Något gick fel");
        return;
      }
      groupElem.remove();
    };

    groupElem.innerHTML = group;
    groupElem.appendChild(deleteButton);
    document.getElementById("groupList").appendChild(groupElem);
  }
}
