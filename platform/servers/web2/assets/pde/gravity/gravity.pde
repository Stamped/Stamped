/*! gravity.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing
 */

static int SIMULATION_WIDTH         = /** int ( 0, 1024 ] **/ 640 /** endint **/;
static int SIMULATION_HEIGHT        = /** int ( 0, 1024 ] **/ 480 /** endint **/;

static int DEFAULT_GRAVITY_SPEED    = /** int [ 300, 1000 ] **/ 900 /** endint **/;
static int MAX_GRAVITY_SPEED        = 1000;

static int NUMBER_OF_PARTICLES      = /** int [ 12, 300 ] **/ 150 /** endint **/;

// scaling factor that affects the mass of the bodies, effectively scaling the 
// overall gravity strength of the system.
int simulationSpeed;

// bodies in the system are spawned in either a radial or random fashion
int initialState;

// global array of body particles in the simulation
Body[] bodies;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(30);
    smooth();
    loop();
    
    bodies          = new Body[NUMBER_OF_PARTICLES];
    simulationSpeed = DEFAULT_GRAVITY_SPEED;
    initialState    = /** int [ 0, 1 ] **/ 0 /** endint **/;
    
    reset();
}

void reset() {
    int num_particles = bodies.length;
    
    if (initialState == 1) {
        // initial state of bodies arranged randomly
        for(int i = 0; i < num_particles; i++) {
            bodies[i] = new Body();
        }
    } else {
        float x0 = width  / 2.0;
        float y0 = height / 2.0;
        float r0 = sqrt(width * width + height * height) / 4.5;
        
        // initial state of bodies arranged in a circular fashion
        for(int i = 0; i < num_particles; i++) {
            float theta = i * TWO_PI / num_particles;
            float x = x0 + r0 * cos(theta);
            float y = y0 + r0 * sin(theta);
            
            bodies[i] = new Body(x, y);
        }
    }
}

void draw() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    update();
    
    for(int i = 0; i < bodies.length; i++) {
        bodies[i].draw();
    }
}

void update() {
    int num_particles = bodies.length;
    
    // for each body in the system, enact a force on every other body in the system
    // running time O(num_particles ^ 2)
    for(int i = 0; i < num_particles; i++) {
        for(int j = i + 1; j < num_particles; j++) {
            float xDif = bodies[j]._x - bodies[i]._x;
            float yDif = bodies[j]._y - bodies[i]._y;
            float invDistSquared = 1.0 / (xDif * xDif + yDif * yDif);
            
            // force is inversely proportional to the distance squared
            xDif *= invDistSquared;
            yDif *= invDistSquared;
            
            bodies[i].addAcceleration( xDif * bodies[j]._mass,  yDif * bodies[j]._mass);
            bodies[j].addAcceleration(-xDif * bodies[i]._mass, -yDif * bodies[i]._mass);
        }
    }
    
    for(int i = 0; i < bodies.length; i++) {
        bodies[i].update();
    }
}

class Body {
    // position
    float _x;
    float _y;
    
    // velocity vector <_dX, _dY>
    float _dX, _dY;
    
    // affects this body's gravitational pull w.r.t. other bodies
    float _mass;
    float _weight;
    float _size;
    
    // fill color of this body
    color _fill;
    
    // creates a body at a random location and random mass
    Body() {
        this(random(width  / 4.0, 3 * width  / 4.0), 
             random(height / 4.0, 3 * height / 4.0));
    }
    
    // creates a body at a given location with a random mass
    Body(float x, float y) {
        this(x, y, random(10, 45));
    }
    
    // creates a body at the given location with the given mass
    Body(float x, float y, float mass) {
        _x = x;
        _y = y;
        
        _dX = 0.0;
        _dY = 0.0;
        
        _size   = mass;
        _weight = random(/** float [ .2, 5 ] **/ 1.0 /** endfloat **/, 
                         /** float [ 1,  6 ] **/ 3.0 /** endfloat **/);
        
        // select a random color from within a predefined color palette
        int offset = 3 * int(random(0.0, (PALETTE.length - 1) / 3.0));
        _fill      = color(PALETTE[offset], 
                           PALETTE[offset + 1], 
                           PALETTE[offset + 2], 48);
        
        resetMass();
    }
    
    void resetMass() {
        _mass = _size / (MAX_GRAVITY_SPEED - simulationSpeed);
    }
    
    void addAcceleration(float accelX, float accelY) {
        _dX += accelX;
        _dY += accelY;
    }
    
    boolean update() {
        _x += _dX;
        _y += _dY;
        
        return true;
    }
    
    // returns whether or not this body intersects the given body (currently unused)
    boolean intersects(Body body) {
        float radius = (_size / 2);
        float rad    = (body._size / 2);
        float xDif   = body._x - _x;
        float yDif   = body._y - _y;
        float dist   = sqrt(xDif * xDif + yDif * yDif);
        
        // reject if dist btwn circles is greater than their radii combined
        if (dist > radius + rad) {
            return false;
        }
        
        // reject if one circle is inside of the other
        return (dist >= abs(rad - radius));
    }
    
    void draw() {
        fill(_fill);
        stroke(/** color **/ color(0, 0, 0, 78) /** endcolor **/);
        strokeWeight(_weight);
        
        ellipse(_x, _y, _size, _size);
    }
}

// color palette extracted from a seed image
static int[] PALETTE = {
    0, 0, 0, 0, 16, 0, 104, 104,
    112, 104, 112, 120, 104, 88, 88, 112, 128, 128, 120, 120, 128, 128,
    88, 0, 144, 104, 72, 144, 80, 72, 144, 88, 24, 144, 96, 112, 152,
    104, 112, 152, 160, 184, 152, 48, 16, 152, 64, 8, 16, 0, 0, 16, 32,
    40, 160, 112, 120, 160, 120, 0, 160, 120, 72, 160, 128, 120, 160,
    144, 120, 160, 160, 168, 160, 56, 16, 160, 88, 16, 168, 144, 112,
    168, 152, 104, 168, 152, 72, 168, 160, 120, 168, 168, 128, 168,
    176, 160, 168, 40, 24, 176, 136, 104, 176, 144, 32, 176, 144, 48,
    176, 160, 152, 176, 168, 112, 176, 168, 144, 176, 176, 120, 176,
    176, 152, 176, 184, 176, 176, 192, 184, 184, 136, 104, 184, 184,
    168, 184, 184, 176, 192, 152, 136, 192, 160, 96, 192, 176, 120,
    192, 176, 144, 192, 192, 144, 192, 192, 176, 200, 160, 120, 200,
    176, 120, 200, 176, 96, 200, 184, 160, 200, 192, 152, 200, 200,
    184, 208, 176, 120, 208, 176, 128, 208, 176, 176, 208, 184, 144,
    208, 192, 160, 208, 192, 88, 208, 200, 160, 208, 200, 168, 208,
    200, 176, 208, 208, 192, 216, 192, 112, 216, 192, 136, 216, 192,
    160, 216, 192, 168, 216, 192, 176, 216, 200, 152, 216, 200, 160,
    216, 200, 176, 216, 208, 176, 224, 160, 96, 224, 176, 128, 224,
    184, 80, 224, 200, 160, 224, 200, 168, 224, 200, 88, 224, 208, 152,
    224, 208, 160, 224, 208, 176, 224, 216, 160, 224, 216, 176, 224,
    216, 184, 224, 224, 176, 224, 224, 184, 224, 224, 192, 232, 184,
    120, 232, 184, 40, 232, 192, 120, 232, 192, 136, 232, 200, 128,
    232, 200, 152, 232, 200, 72, 232, 208, 120, 232, 208, 80, 232, 216,
    168, 232, 216, 192, 232, 216, 200, 232, 224, 128, 232, 224, 152,
    232, 224, 176, 232, 224, 200, 232, 232, 216, 232, 240, 192, 232,
    240, 216, 232, 240, 224, 240, 200, 104, 240, 200, 152, 240, 208,
    152, 240, 216, 112, 240, 216, 144, 240, 216, 152, 240, 216, 192,
    240, 216, 208, 240, 224, 128, 240, 224, 176, 240, 224, 184, 240,
    224, 192, 240, 232, 160, 240, 232, 184, 240, 232, 192, 240, 232,
    200, 240, 232, 208, 240, 232, 216, 240, 240, 192, 240, 240, 200,
    240, 240, 208, 240, 240, 224, 240, 248, 168, 248, 184, 136, 248,
    184, 40, 248, 224, 112, 248, 224, 160, 248, 224, 168, 248, 224,
    176, 248, 224, 184, 248, 224, 192, 248, 224, 80, 248, 232, 120,
    248, 232, 184, 248, 232, 192, 248, 232, 208, 248, 232, 224, 248,
    240, 184, 248, 240, 200, 248, 240, 208, 248, 240, 216, 248, 248,
    208, 255, 152, 40, 255, 200, 40, 255, 208, 112, 255, 208, 184, 255,
    208, 40, 255, 216, 160, 255, 216, 168, 255, 216, 176, 255, 224,
    120, 255, 232, 104, 255, 232, 120, 255, 232, 144, 255, 232, 152,
    255, 232, 176, 255, 232, 184, 255, 232, 192, 255, 240, 152, 255,
    240, 160, 255, 240, 184, 255, 248, 176, 48, 32, 8, 56, 40, 16, 56,
    56, 40, 56, 64, 48, 72, 72, 88, 80, 16, 0, 80, 88, 96, 88, 104,
    104, 88, 104, 88, 88, 40, 0, 88, 80, 72, 88, 88, 56, 96, 112, 112,
    96, 56, 16, 
};

