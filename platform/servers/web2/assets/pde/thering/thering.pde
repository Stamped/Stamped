/*! thering.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Original concept and code by J. Tarbell
 * <a href="http://www.complexification.net/gallery/machines/binaryRing/">Complexification</a>
 */

static int SIMULATION_WIDTH  = 640;
static int SIMULATION_HEIGHT = 480;

color BLOOD_COLOR = color(0xBF, 0x21, 0x07, 0x18); // dark red

int _noRingParticles;
int _originRadius;

ArrayList _ringParticles;

// Color that new particles will be drawn when respawned
boolean _blackout;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(60);
    smooth();
    loop();
    
    reset();
}

void reset() {
    background(#000000);
    
    _noRingParticles = 5000;
    _originRadius    = 50;
    _ringParticles   = new ArrayList(_noRingParticles);
    _blackout        = false;
    
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
    if (random(0.0, 1.0) > 0.995) {
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
        
        int alpha = 24;
        
        // transparent black or white
        _color = (_blackout ? color(0, 0, 0, alpha) : color(255, 255, 255, alpha));
        _age   = int(random(0, 200));
    }
    
    void update() {
        // record Particle's Old Position
        int oldX = (int)_x, oldY = (int)_y;
        
        // update Particle's Position
        _x += _dX;
        _y += _dY;
        
        // apply slight, random changes to Particle's Velocity
        _dX += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5f;
        _dY += (random(0.0, 1.0) - random(0.0, 1.0)) * 0.5f;
        
        if (oldX != (int)_x || oldY != (int)_y) {
            // randomly intersperse blood color with Black
            if (int(red(_color)) == 255 && random(0.0, 1.0) > 0.95) {
                stroke(BLOOD_COLOR);
            } else {
                stroke(_color);
            }
            
            // draw a line connecting old particle's Position to new Position
            line(oldX, oldY, _x, _y);
            
            if (_x < 0 || _x >= width || _y < 0 || _y >= height || ++_age > 200) {
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
        
        int alpha = 24;
        
        _age   = 0;
        _color = (_blackout ? color(0, 0, 0, alpha) : color(255, 255, 255, alpha));
    }
}

