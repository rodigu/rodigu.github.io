let vnt = false;
let phrase = "This sentence will write itself slowly";
let counter = 0;
function setup(){
  frameRate(50);
  canvas1 = createCanvas(100, 100);
  paragraph = createElement('h1', "Current time: " + hour());
  follow = createElement('h1', "&#129409; <br> i will follow u *o*");
}

function draw(){
  if (millis() >= 1000 && !vnt){
    vnt = true;
    paragraph.html("");
  }
  if (vnt && counter < phrase.length && frameCount%int(random(3, 6)) == 0){
    paragraph.html(phrase[counter], true);
    counter++;
  }
  follow.position(mouseX + 50,mouseY + 50);
  background(255);
  fill(230);
  ellipse(50, 50, 50, 50);
}
