/*
let vnt = false;
var counter = 0;
let phrase = "This sentence will write itself slowly";
var leon;
function setup(){
  frameRate(50);
  canvas1 = createCanvas(100, 100);
  input = createInput("Leon");
  fbutton = createButton("Update text");
  sizeslide = createSlider(20, 500, 50);
  paragraph = createElement('h1', "Current time: " + hour());
  leon = new Emoji(mouseX, mouseY, "assets/dancin.gif", "Leon");
}

function nameChange(){
  leon.name = input.value();
}
function draw(){
  leon.s = sizeslide.value();
  leon.movement(mouseX + 10, mouseY + 150);
  fbutton.mousePressed(nameChange);
  leon.update();
  if (millis() >= 1000 && !vnt){
    vnt = true;
    counter = 0;
    paragraph.html("...");
  }
  if (vnt && counter < phrase.length && frameCount%int(random(3, 6)) == 0){
    paragraph.html(phrase[counter], true);
    counter++;
  }
  if (counter >= phrase.length && frameCount%100 == 0) vnt = false;
  fill(230);
  ellipse(50, 50, 50, 50);
}
*/
