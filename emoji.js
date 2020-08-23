class Emoji{
  constructor(x_, y_, img_, name_, s_){
    this.x = x_;
    this.y = y_;
    this.name = name_;
    this.s = s_;
    this.img = createImg(img_, "");
    this.img.size(s_, 1.5*s_);
    this.text = createElement('h1', this.name);
  }
  update(){
    this.text.html(this.name);
    this.img.size(this.s, 1.5*this.s);
  }
  movement(x_, y_){
    this.text.position(x_, y_ - 50);
    this.img.position(x_ - this.s/2, y_);
  }
}
