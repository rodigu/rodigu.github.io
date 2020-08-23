let vnt = false;
let phrase = "This sentence will write itself slowly";
let counter;
let move = true;
function setup(){
  frameRate(50);
  canvas1 = createCanvas(100, 100);
  paragraph = createElement('h1', "Current time: " + hour());
  follow = createElement('h1', "&#129409;<br>i will follow u >:D");
  fbutton = createButton("Following Lion");
}

function movedec(){
  if (move){
    move = false;
    follow.html("&#129409;<br>i stop following*_*");
  }
  else{
    move = true;
    follow.html("&#129409;<br>i will follow u >:D");
  }
}

// function mousePressed(){
//   console.log(follow.position(), '\n', mouseX, ' ', mouseY);
//   console.log('\n', canvas1.position());
//   move = false;
// }
// function mouseReleased(){
//   move = true;
// }

function draw(){
  fbutton.mousePressed(movedec);
  if (millis() >= 1000 && !vnt){
    vnt = true;
    counter = 0;
    paragraph.html(" ");
  }
  if (vnt && counter < phrase.length && frameCount%int(random(3, 6)) == 0){
    paragraph.html(phrase[counter], true);
    counter++;
  }
  if (counter >= phrase.length && frameCount%100 == 0) vnt = false;
  if (move) follow.position(mouseX + 8, mouseY + 110);
  background(255);
  fill(230);
  ellipse(50, 50, 50, 50);
}
