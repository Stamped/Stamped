/*! substrate.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Original Concept and code by J. Tarbell
 * <a href="http://www.complexification.net/gallery/machines/tremaSpike/">Complexification</a>
 */

static int SIMULATION_WIDTH     = /** int ( 0, 1024 ] **/ 640 /** endint **/;
static int SIMULATION_HEIGHT    = /** int ( 0, 1024 ] **/ 480 /** endint **/;

float _dimLog;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    smooth();
    frameRate(60);
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #000000 /** endcolor **/);
    
    _dimLog = log(width);
}

void draw() {
    float scale = /** float [ 0, 10 ] **/ 1 /** endfloat **/;
    float x = random(0, width);
    float y = random(0, height);
    float a = random(20, 255);
    
    scale += /** float [ 1, 100 ] **/ 10 /** endfloat **/ * (_dimLog - log(1 + random(0.0, width)));
    
    stroke(/** color **/ color(255, 255, 255, 0) /** endcolor **/);
    fill(/** color **/ color(255, 255, 255, a) /** endcolor **/);
    
    if (random(0.0, 1.0) < /** float [ 0, 1 ] **/ 0.5 /** endfloat **/) {
        ellipse(x, y, scale, scale);
    } else {
        rect(x, y, scale, scale);
    }
}

void mouseClicked() {
    reset();
}

