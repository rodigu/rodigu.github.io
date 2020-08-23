let vnt = false;
let phrase = "This sentence will write itself slowly";
let counter;
let move = true;
function setup(){
  frameRate(50);
  canvas1 = createCanvas(100, 100);
  paragraph = createElement('h1', "Current time: " + hour());
  follow = createElement('h1', "&#129409; <br> i will follow u *o*");
}

function mousePressed(){
  console.log(follow.position(), '\n', mouseX, ' ', mouseY);
  move = false;
}
function mouseReleased(){
  move = true;
}

function draw(){
  if (millis() >= 1000 && !vnt){
    vnt = true;
    counter = 0;
    paragraph.html("");
  }
  if (vnt && counter < phrase.length && frameCount%int(random(3, 6)) == 0){
    paragraph.html(phrase[counter], true);
    counter++;
  }
  if (counter >= phrase.length && frameCount%100 == 0) vnt = false;
  if (move) follow.position(mouseX + 20, mouseY + 60);
  background(255);
  fill(230);
  ellipse(50, 50, 50, 50);
}
