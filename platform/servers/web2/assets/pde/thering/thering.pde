/*! thering.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Original concept and code by J. Tarbell
 * <a href="http://www.complexification.net/gallery/machines/binaryRing/">Complexification</a>
 */

static int SIMULATION_WIDTH     = /** int ( 0, 1024 ] **/ 640 /** endint **/;
static int SIMULATION_HEIGHT    = /** int ( 0, 1024 ] **/ 480 /** endint **/;

static int PARTICLE_MAX_AGE     = /** int [ 10, 500 ] **/ 200 /** endint **/;
static int PARTICLE_ALPHA       = /** int [ 10, 255 ] **/ 24  /** endint **/;

color BLOOD_COLOR = /** color **/ color(0xBF, 0x21, 0x07, 0x18) /** endcolor **/; // dark red

int _noRingParticles;
int _originRadius;

ArrayList _ringParticles;

// controls newly spawned particle color
boolean _blackout;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(60);
    smooth();
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #000000 /** endcolor **/);
    
    _noRingParticles = /** int [ 50, 50000 ] **/ 5000  /** endint **/;
    _originRadius    = /** int [ 0, 250 ]    **/ 50    /** endint **/;
    _blackout        = /** boolean **/           false /** endboolean **/;
    
    _ringParticles   = new ArrayList(_noRingParticles);
    
    float theta = TWO_PI * random(0.0, 1.0);
    float thetaAdd = (random(0.0, 1.0) * 4 + TWO_PI) / _noRingParticles;
    _ringParticles.clear();
    
    // Initial particles sling-shot around ring origin
    for(int i = 0; i < _noRingParticles; i++, theta += thetaAdd) {
        float emitX = (width  / 2) + _originRadius * sin(theta);
        float emitY = (height / 2) + _originRadius * cos(theta);
        
        _ringParticles.add(new RingParticle(emitX, emitY, theta / 2));
    }
}

void draw() {
    // Move and Draw all of the RingParticles
    for (int i = 0; i < _ringParticles.size(); i++) {
        RingParticle particle = ((RingParticle) _ringParticles.get(i));
        particle.update();
    }
    
    // Randomly switch between blackout periods
    if (random(0.0, 1.0) > /** float [ 0, 1 ] **/ 0.995 /** endfloat **/) {
        _blackout = !_blackout;
    }
}

void mouseClicked() {
    _blackout = !_blackout;
}

void setOriginRadius(int newRadius) {
    if (newRadius > 0) {
        _originRadius = newRadius;
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
        // record Particle's Old Position
        int oldX = (int)_x, oldY = (int)_y;
        
        // update Particle's Position
        _x += _dX;
        _y += _dY;
        
        // apply slight, random changes to Particle's Velocity
        _dX += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5;
        _dY += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5;
        
        if (oldX != (int)_x || oldY != (int)_y) {
            // randomly intersperse blood color with Black
            if (int(red(_color)) == 255 && random(0.0, 1.0) > 0.95) {
                stroke(BLOOD_COLOR);
            } else {
                stroke(_color);
            }
            
            // draw a line connecting old particle's Position to new Position
            line(oldX, oldY, _x, _y);
            
            if (_x < 0 || _x >= width || _y < 0 || _y >= height || ++_age > PARTICLE_MAX_AGE) {
                this.respawn();
            }
        }
    }
    
    // Die and be reborn
    void respawn() {
        float theta = TWO_PI * random(0.0, 1.0);
        
        // initial Position of new Particle on Radius of Origin
        _x = (width  / 2) + _originRadius * sin(theta);
        _y = (height / 2) + _originRadius * cos(theta);
        
        // reset initial velocity to zero
        _dX = 0;
        _dY = 0;
        
        _age   = 0;
        _color = (_blackout ? color(0, 0, 0, PARTICLE_ALPHA) : color(255, 255, 255, PARTICLE_ALPHA));
    }
}

