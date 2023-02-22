const generateCard = (
  parentElement,
  args = {
    hrefLink: "https://deno.land/x/nets",
    title: "NeTS",
    description:
      "Network Science library. Currently used for research on trade cycles in currency markets.",
    languageLogo:
      "https://upload.wikimedia.org/wikipedia/commons/4/4c/Typescript_logo_2020.svg",
    topImage: "./imgs/denologo.png",
    bottomImage: "./imgs/netscode.png",
  }
) => {
  const { hrefLink, title, description, languageLogo, topImage, bottomImage } =
    args;
  const newCard = document.createElement("div");

  newCard.classList.add("card");
  newCard.innerHTML = `
    <a href="${hrefLink}" target="_blank">
      <div class="cart-title">
        <h2>
          ${title}<img
            class="langlogo"
            src="${languageLogo}"
          />
        </h2>
      </div>
      <p>${description}</p>
      <div>
        <img class="overimg" src="${topImage}" />
        <img class="underimg" src="${bottomImage}" />
      </div>
    </a>
  `;

  parentElement.appendChild(newCard);
};

let leftButton = document.getElementById("leftbutton");
let rightButton = document.getElementById("rightbutton");
let centralButton = document.getElementById("centralbutton");

let gamesSection = document.getElementById("games");
let workSection = document.getElementById("work");
let projectsSection = document.getElementById("projects");

let sectionOrder = new Map();
sectionOrder.set("projects", projectsSection);
sectionOrder.set("work", workSection);
sectionOrder.set("games", gamesSection);

function changeSection(buttonChosen) {
  let sectionKeys = [...sectionOrder.keys()];

  let [left, center, right] = sectionKeys;

  console.log(buttonChosen);

  if (buttonChosen === left) {
    direction = "left";
  } else if (buttonChosen === right) {
    direction = right;
  }

  let menuOrder = ["left", "center", "right"];

  for (idx in sectionKeys) {
    key = sectionKeys[idx];
    sectionOrder.get(key).dataset.status = menuOrder[idx];
  }

  if (buttonChosen === "projects")
    sectionOrder.get("work").dataset.status = "right";
  else sectionOrder.get("work").dataset.status = "left";

  sectionOrder.get(buttonChosen).dataset.status = "center";
}
