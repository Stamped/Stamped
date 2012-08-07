
Body[] bodies;

// Scaling factor that affects the mass of the Bodies, effectively scaling 
// the force a Body enacts on another Body
int simulationSpeed;

// Drawing variation (either clean or aggregate)
int variation;

// Bodies in the system are spawned in either a radial or random fashion
int initialState;

static int SIMULATION_WIDTH  = 640;
static int SIMULATION_HEIGHT = 480;

static int PARTICLE_ORIGIN_X = SIMULATION_WIDTH  / 2.0;
static int PARTICLE_ORIGIN_Y = SIMULATION_HEIGHT / 2.0;

static int DEFAULT_GRAVITY_SPEED        = 900;
static int MAX_GRAVITY_SPEED            = 1000;
static int DEFAULT_GRAVITY_NO_PARTICLES = 100;
static int MAX_GRAVITY_NO_PARTICLES     = 300;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(24);
    stroke(#000000);
    fill(#FFFFFF);
    smooth();
    loop();
    
    bodies          = new Body[DEFAULT_GRAVITY_NO_PARTICLES];
    simulationSpeed = DEFAULT_GRAVITY_SPEED;
    variation       = 0;
    initialState    = 0;
    
    reset();
}

void reset() {
    int num_particles = bodies.length();
    
    if (initialState == 1) {
        // Initial State of Bodies arranged randomly
        for(int i = 0; i < num_particles; i++) {
            bodies[i] = new Body();
        }
    } else {
        // Initial State of Bodies arranged in a Circular fashion
        for(int i = 0; i < num_particles; i++) {
            float theta = i * TWO_PI / num_particles;
            float x = PARTICLE_ORIGIN_X + 150 * cos(theta);
            float y = PARTICLE_ORIGIN_Y + 150 * sin(theta);
            
            bodies[i] = new Body(x, y);
        }
    }
}

void draw() {
    background(#FFFFFF);
    update();
    
    for(int i = 0; i < bodies.length(); i++) {
        bodies[i].draw();
    }
}

void update() {
    num_particles = bodies.length();
    
    // For each body in the system, enact a force on every 
    // other body in the system; Running time O(num_particles ^ 2)
    for(int i = 0; i < num_particles; i++) {
        for(int j = i + 1; j < num_particles; j++) {
            float xDif = bodies[j]._x - bodies[i]._x;
            float yDif = bodies[j]._y - bodies[i]._y;
            float invDistSquared = 1.0 / (xDif * xDif + yDif * yDif);
            
            // Force is inversely proportional to the distance squared
            xDif *= invDistSquared;
            yDif *= invDistSquared;
            
            bodies[i].addAcceleration(xDif * bodies[j]._mass, 
                                       yDif * bodies[j]._mass);
            bodies[j].addAcceleration(-xDif * bodies[i]._mass, 
                                       -yDif * bodies[i]._mass);
        }
    }
    
    for(int i = 0; i < bodies.length(); i++) {
        bodies[i].update();
    }
}

static int[] SUBSTRATE_COLORS = {
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

class Body {
    // Position
    float _x;
    float _y;
    
    // Velocity vector <_dX, _dY>
    float _dX, _dY;
    float _mass;
    float _size;
    
    color _color;
    float _weight;
    
    /*
     * Creates a Body at a random location
     */
    Body() {
        this(random(SIMULATION_WIDTH / 4.0, 3 * SIMULATION_WIDTH / 4.0), 
             random(SIMULATION_HEIGHT / 4.0, 3 * SIMULATION_HEIGHT / 4.0));
    }
    
    /*
     * Creates a body at a given location with a random mass
     */
    Body(float x, float y) {
        this(x, y, random(10, 45));
    }
    
    /*
     * Creates a body at the given location with the given mass
     */
    Body(float x, float y, float mass) {
        this._x = x;
        this._y = y;
        this._size = mass;
        
        this._dX = 0.0;
        this._dY = 0.0;
        
        this.resetMass();
        
        int offset   = 3 * int(random(0.0, (SUBSTRATE_COLORS.length() - 1) / 3.0));
        this._color  = color(SUBSTRATE_COLORS[offset], SUBSTRATE_COLORS[offset + 1], SUBSTRATE_COLORS[offset + 2], 48);
        this._weight = random(1.0, 3.0);
    }
    
    /* _mass effects how fast bodies will be pulled towards each other, and 
     * by globally scaling the masses of all of the bodies in the system
     * (with simulationSpeed), the 'speed' of the simulation can be changed 
     */ 
    void resetMass() {
        this._mass = this._size / (MAX_GRAVITY_SPEED - simulationSpeed);
    }
    
    void addAcceleration(float accelX, float accelY) {
        this._dX += accelX;
        this._dY += accelY;
    }
    
    boolean update() {
        this._x += this._dX;
        this._y += this._dY;
        
        return true;
    }
    
    // Returns whether or not this Body intersects the given Body (currently unused)
    boolean intersects(Body body) {
        float radius = (this._size / 2);
        float rad    = (body._size / 2);
        float xDif = body._x - _x;
        float yDif = body._y - _y;
        float dist = sqrt(xDif * xDif + yDif * yDif);
        
        // Reject if dist btwn circles is greater than their radii combined
        if (dist > radius + rad) {
            return false;
        }
        
        // Reject if one circle is inside of the other
        return (dist >= abs(rad - radius));
    }
    
    void draw() {
        int size = this._size / 2.0;
        float x = _x - size;
        float y = _y - size;
        
        // Select a random color from within a predefined color palette
        fill(this._color);
        stroke(0, 0, 0, 78);
        strokeWeight(this._weight);
        
        ellipse(x, y, this._size, this._size);
    }
}

