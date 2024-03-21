const langs = {
  js: "./imgs/jslogo.jpeg",
  py: "https://cdn4.iconfinder.com/data/icons/scripting-and-programming-languages/512/Python_logo-512.png",
  lua: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Lua-Logo.svg/1200px-Lua-Logo.svg.png",
  blocki: "./imgs/blocki.png",
};

function addProjects() {
  generateCard(document.getElementById("projects"), {
    hrefLink: "https://github.com/rodigu/supernova-age",
    title: "Supernova Age Prediction",
    description:
      "Applying Machine-Learning clustering algorithms to help predict the age of supernovae.",
    languageLogo: langs.py,
    topImage: "",
    bottomImage: "",
    year: "Fall 2022",
  });

  generateCard(document.getElementById("projects"), {
    hrefLink: "https://github.com/Liu-Hy/Food-Bank-Network-Simulation",
    title: "Foodbank Simulation",
    description:
      "Monte Carlo simulation of food distribution networks by foodbanks. Built based on real data from Illinois Foodbanks",
    languageLogo: langs.py,
    topImage: "",
    bottomImage: "",
    year: "Fall 2022",
  });

  generateCard(document.getElementById("projects"), {
    hrefLink: "https://tic80.com/play?cart=2788",
    title: "WFC",
    description:
      "Wave function collapse algorithm implemented inside a TIC-80 retro fantasy console.",
    languageLogo: langs.lua,
    topImage: "./imgs/wfcgifcover.gif",
    bottomImage: "./imgs/wfccover.png",
    year: "Spring 2022",
  });

  generateCard(document.getElementById("projects"), {
    hrefLink: "https://tic80.com/play?cart=2897",
    title: "RPS Cellular Automata",
    description: "Implementation of the Rock-Paper-Scissors cellular automata.",
    languageLogo: langs.lua,
    topImage: "./imgs/rpsca.gif",
    bottomImage: "./imgs/rpsca.gif",
    year: "Fall 2022",
  });
}

function addWork() {
  generateCard(document.getElementById("work"), {
    hrefLink: "http://catalog.illinois.edu/courses-of-instruction/gsd/",
    title: "GSD 103 TA",
    description:
      "Teaching assistant for Basics of Game Design. Taught and graded two discussion sessions (30 students).",
    languageLogo: langs.blocki,
    topImage: "",
    bottomImage: "",
    year: "Spring 2023",
  });

  generateCard(document.getElementById("work"), {
    hrefLink: "https://ischool.illinois.edu/degrees-programs/courses/is101",
    title: "IS 101 TA",
    description:
      "Teaching assistant for Information Science 101. Taught and graded two discussion sessions (50 students).",
    languageLogo: langs.blocki,
    topImage: "",
    bottomImage: "",
    year: "Fall 2022",
  });

  generateCard(document.getElementById("work"));

  generateCard(document.getElementById("work"), {
    hrefLink: "https://pushstart.com.br",
    title: "Software Developer",
    description:
      "Junior JS developer at PushStart. Implemented web-based games using the PixiJS library.",
    languageLogo: langs.js,
    topImage: "",
    bottomImage: "",
    year: "Fall 2021",
  });
}

function addGames() {
  generateCard(document.getElementById("games"), {
    hrefLink: "https://rmorais.itch.io/matic",
    title: "MaTIC",
    description: "Educational math game.",
    languageLogo: langs.lua,
    topImage: "./imgs/matic.gif",
    bottomImage: "./imgs/matic_play.gif",
    year: "Fall 2024",
  });

  generateCard(document.getElementById("games"), {
    hrefLink: "https://rmorais.itch.io/xadado",
    title: "Xadado",
    description:
      "A dice board game for two. Made for TIC-80 retro fantasy console.",
    languageLogo: langs.lua,
    topImage: "./imgs/dademomenu.gif",
    bottomImage: "./imgs/dademoplay.gif",
    year: "Spring 2023",
  });

  generateCard(document.getElementById("games"), {
    hrefLink: "https://tic80.com/play?cart=2922",
    title: "Batchan Game",
    description: "Tic-tac-toe variation for the TIC-80 fantasy console.",
    languageLogo: langs.lua,
    topImage: "./imgs/baga.gif",
    bottomImage: "./imgs/baga.gif",
    year: "Fall 2022",
  });

  generateCard(document.getElementById("games"), {
    hrefLink: "https://rmorais.itch.io/deliveries-bitsy",
    title: "Deliveries",
    description:
      "Bitsy game about making deliveries to friends from around the world.",
    languageLogo: langs.js,
    topImage: "./imgs/deliveriescover.png",
    bottomImage: "./imgs/deliveriesgif.gif",
    year: "Fall 2022",
  });

  generateCard(document.getElementById("games"), {
    hrefLink: "https://rmorais.itch.io/ntro",
    title: "ntro",
    description:
      "Tron-like game for an arbitrary number of players. Made in 3 hours for Trijam #153.",
    languageLogo: langs.js,
    topImage: "./imgs/ntrocover.png",
    bottomImage: "./imgs/ntrocover.png",
    year: "Spring 2022",
  });

  generateCard(document.getElementById("games"), {
    hrefLink: "https://rmorais.itch.io/a-monstrous-constelation",
    title: "Monstrous Constelation",
    description:
      "Implementation of chirp-firing/dollar game. Made using the Network2020 library.",
    languageLogo: langs.js,
    topImage: "./imgs/monstrouscover.png",
    bottomImage: "./imgs/monstrousgif.gif",
    year: "Spring 2022",
  });
}

addWork();
addGames();
addProjects();
