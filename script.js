const generateCard = (
  parentElement,
  args = {
    hrefLink: "https://deno.land/x/nets",
    title: "NeTS",
    description: "Deno library for Network Science built in Typescript",
    languageLogo:
      "https://upload.wikimedia.org/wikipedia/commons/4/4c/Typescript_logo_2020.svg",
    topImage: "./imgs/denologo.png",
    bottomImage: "./imgs/netscode.png",
  }
) => {
  const {
    hrefLink,
    title,
    description,
    languageLogo,
    topImage,
    bottomImage,
  } = args;
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

generateCard(document.body);
