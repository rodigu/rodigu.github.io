generateCard(document.getElementById("work"));

generateCard(document.getElementById("games"), {
  hrefLink: "https://rmorais.itch.io/xadado",
  title: "Xadado",
  description:
    "A dice board game for two. Made with the TIC-80 retro fantasy console.",
  languageLogo:
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Lua-Logo.svg/1200px-Lua-Logo.svg.png",
  topImage: "./imgs/dademomenu.gif",
  bottomImage: "./imgs/dademoplay.gif",
});

generateCard(document.getElementById("projects"), {
  hrefLink: "https://github.com/rodigu/supernova-age",
  title: "Supernova Age Prediction",
  description: "Using clustering algorithms to predict the age of supernovae.",
  languageLogo:
    "https://cdn4.iconfinder.com/data/icons/scripting-and-programming-languages/512/Python_logo-512.png",
  topImage: "./imgs/littlestar.png",
  bottomImage: "./imgs/supernovass.png",
});

generateCard(document.getElementById("projects"), {
  hrefLink: "https://github.com/Liu-Hy/Food-Bank-Network-Simulation",
  title: "Foodbank Simulation",
  description: "Monte Carlo simulation of food distribution by foodbanks.",
  languageLogo:
    "https://cdn4.iconfinder.com/data/icons/scripting-and-programming-languages/512/Python_logo-512.png",
  topImage: "./imgs/foodcover.png",
  bottomImage: "./imgs/foodbanksimcode.png",
});

generateCard(document.getElementById("projects"), {
  hrefLink: "https://tic80.com/play?cart=2788",
  title: "WFC",
  description:
    "Wave function collapse algorithm implemented inside a TIC-80 retro fantasy console.",
  languageLogo:
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Lua-Logo.svg/1200px-Lua-Logo.svg.png",
  topImage: "./imgs/wfcgifcover.gif",
  bottomImage: "./imgs/wfccover.png",
});
