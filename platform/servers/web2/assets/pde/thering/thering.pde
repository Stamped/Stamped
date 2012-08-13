/*! thering.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Alternating black and white rings comprised of thousands of particles, all moving 
 * with respect to <a href='http://en.wikipedia.org/wiki/Brownian_motion'>Brownian motion</a>.
 * 
 * Original concept and implementation by J. Tarbell
 * <a href="http://www.complexification.net/gallery/machines/binaryRing/">Complexification</a>
 */

static int NUM_PARTICLES        = /** int [ 50, 50000 ] **/ 5000 /** endint **/;
static int ORIGIN_RADIUS        = /** int [ 0, 250 ]    **/ 50   /** endint **/;

static int PARTICLE_MAX_AGE     = /** int [ 10, 500 ]   **/ 200  /** endint **/;
static int PARTICLE_ALPHA       = /** int [ 10, 255 ]   **/ 24   /** endint **/;

color BLOOD_COLOR = /** color **/ color(0xBF, 0x21, 0x07, 0x18) /** endcolor **/; // dark red

ArrayList _ringParticles;

// controls newly spawned particle color
boolean _blackout;

void setup() {
    size(/** int ( 0, 1024 ] **/ 640 /** endint **/, /** int ( 0, 1024 ] **/ 480 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 24 /** endint **/);
    smooth();
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #000000 /** endcolor **/);
    
    _ringParticles = new ArrayList(NUM_PARTICLES);
    _blackout      = false;
    
    float theta = TWO_PI * random(0.0, 1.0);
    float thetaAdd = (random(0.0, 1.0) * 4 + TWO_PI) / NUM_PARTICLES;
    
    // initial particles sling-shot around ring origin
    for(int i = 0; i < NUM_PARTICLES; i++, theta += thetaAdd) {
        float emitX = (width  / 2) + ORIGIN_RADIUS * sin(theta);
        float emitY = (height / 2) + ORIGIN_RADIUS * cos(theta);
        
        _ringParticles.add(new RingParticle(emitX, emitY, theta / 2));
    }
}

void draw() {
    // move and draw all of the particles
    for (int i = 0; i < _ringParticles.size(); i++) {
        RingParticle particle = ((RingParticle) _ringParticles.get(i));
        particle.update();
    }
    
    // randomly switch between blackout periods
    if (random(0.0, 1.0) > /** float [ 0, 1 ] **/ 0.995 /** endfloat **/) {
        _blackout = !_blackout;
    }
}

void mouseClicked() {
    _blackout = !_blackout;
}

void setOriginRadius(int newRadius) {
    if (newRadius > 0) {
        ORIGIN_RADIUS = newRadius;
    }
}

class RingParticle {
    float _dX, _dY;
    float _x, _y;
    
    int _color;
    int _age;
    
    RingParticle(float x, float y, float theta) {
        // position
        _x = x;
        _y = y;
        
        // velocity
        _dX = 2 * cos(theta);
        _dY = 2 * sin(theta);
        
        // transparent black or white
        _color = (_blackout ? color(0, 0, 0, PARTICLE_ALPHA) : color(255, 255, 255, PARTICLE_ALPHA));
        _age   = int(random(0, PARTICLE_MAX_AGE));
    }
    
    void update() {
        // record particle's old position
        int oldX = (int)_x, oldY = (int)_y;
        
        // update particle's position
        _x += _dX;
        _y += _dY;
        
        // apply slight, random changes to particle's velocity
        _dX += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5;
        _dY += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5;
        
        if (oldX != (int)_x || oldY != (int)_y) {
            // randomly intersperse blood color with black
            if (int(red(_color)) == 255 && random(0.0, 1.0) > 0.95) {
                stroke(BLOOD_COLOR);
            } else {
                stroke(_color);
            }
            
            // draw a line connecting old particle's position to new position
            line(oldX, oldY, _x, _y);
            
            if (_x < 0 || _x >= width || _y < 0 || _y >= height || ++_age > PARTICLE_MAX_AGE) {
                this.respawn();
            }
        }
    }
    
    // die and be reborn
    void respawn() {
        float theta = TWO_PI * random(0.0, 1.0);
        
        // initial position of new particle on radius of origin
        _x = (width  / 2) + ORIGIN_RADIUS * sin(theta);
        _y = (height / 2) + ORIGIN_RADIUS * cos(theta);
        
        // reset initial velocity to zero
        _dX = 0;
        _dY = 0;
        
        _age   = 0;
        _color = (_blackout ? color(0, 0, 0, PARTICLE_ALPHA) : color(255, 255, 255, PARTICLE_ALPHA));
    }
}

