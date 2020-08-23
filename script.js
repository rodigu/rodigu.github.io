let vnt = false;
let phrase = "This sentence will write itself slowly";
let counter = 0;
function setup(){
  frameRate(30);
  canvas1 = createCanvas(100, 100);
  paragraph = createElement('h1', "Current time: " + hour());
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
  background(42);
  fill(230);
  ellipse(50, 50, 50, 50);
}
