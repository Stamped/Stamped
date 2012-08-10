/*! substrate.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Original Concept and code by J. Tarbell
 * <a href="http://www.complexification.net/gallery/machines/tremaSpike/">Complexification</a>
 */

static int SIMULATION_WIDTH     = 640;
static int SIMULATION_HEIGHT    = 480;

float _dimLog;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    smooth();
    frameRate(60);
    loop();
    
    reset();
}

void reset() {
    background(#000000);
    
    _dimLog = log(width);
}

void draw() {
    float scale = 1 + 10 * (_dimLog - log(1 + random(0.0, width)));
    float x = random(0, width);
    float y = random(0, height);
    
    stroke(color(255, 255, 255, 0));
    fill(255, 255, 255, random(20, 255));
    
    float rand = random(0.0, 1.0);
    
    if (rand < 0.5) {
        ellipse(x, y, scale, scale);
    } else {
        rect(x, y, scale, scale);//, random(0.0, scale / 2.0));
    }
}

void mouseClicked() {
    reset();
}

