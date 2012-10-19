/*! tenebrous.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing
 * 
 * Recursive "tree" branches.
 */

static int NUM_INITIAL_TREES    = /** int [ 1,  32  ]   **/ 5    /** endint **/;

static float MAX_TREE_SIZE      = /** float [ 10, 180 ] **/ 60   /** endfloat **/;
static float MIN_TREE_SIZE      = /** float [ 0.5, 5  ] **/ 1.5  /** endfloat **/;
static float PARTICLE_SPEED     = /** float [ 0.1, 20 ] **/ 3.33 /** endfloat **/;

static int MAX_SIMULATION_AGE   = /** int [ 10, inf ]   **/ 800  /** endint **/;

ArrayList particles;

int age;

void setup() {
    size(/** int ( 0, 1024 ] **/ 640 /** endint **/, /** int ( 0, 1024 ] **/ 480 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 24 /** endint **/);
    smooth();
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    
    particles = new ArrayList();
    age = 0;
    
    for (int i = 0; i < NUM_INITIAL_TREES; i++) {
        particles.add(new Particle());
    }
}

void draw() {
    update();
    
    for(int i = 0; i < particles.size(); i++) {
        ((Particle) particles.get(i)).draw();
    }
}

void update() {
    if (++age > MAX_SIMULATION_AGE) {
        reset();
    }
    
    for(int i = 0; i < particles.size(); i++) {
        Particle particle = ((Particle) particles.get(i));
        
        if (!particle.update()) {
            particles.remove(i);
        }
    }
}

void mouseClicked() {
    particles.add(new Particle(mouseX, mouseY));
}


class Particle {
    // position
    float _x;
    float _y;
    
    // direction
    float _theta;
    float _dTheta;
    
    // current thickness
    float _size;
    
    // number of frames until this particle will branch next
    int _length;
    
    // particle's fill color
    color _fill;
    
    // creates a particle at a random location and size
    Particle() {
        this(random(0.0, width - 1.0), random(0.0, height - 1.0));
    }
    
    // creates a particle with a random size
    Particle(float x, float y) {
        this(x, y, random(0.0, TWO_PI), random(30, MAX_TREE_SIZE));
    }
    
    // creates a new particle
    Particle(float x, float y, float theta, float size) {
        _x = x;
        _y = y;
        
        _theta  = theta;
        _dTheta = random(-0.005, 0.005);
        _size   = size;
        
        _reset_color();
        _reset_length();
    }
    
    // returns a new particle spawned from the given trunk
    static Particle _spawn(Particle trunk) {
        return Particle._spawn(trunk, (random(0.0, 1.0) < 0.5));
    }
    
    // returns a new particle spawned from the given trunk
    static Particle _spawn(Particle trunk, boolean sign) {
        return new Particle(trunk._x, trunk._y, trunk._theta + (sign ? 1 : -1) * 
                            (random(10.0, MAX_TREE_SIZE - 10.0)) * 180.0 / PI, 
                            random(trunk._size * (2.0 / 3.0), trunk._size + log(trunk._size) / 8.0));
    }
    
    private void _reset_color() {
        // 50% of the time, make the particle black
        if (random(0.0, 1.0) > /** float [ 0, 1 ] **/ 0.5 /** endfloat **/) {
            _fill = /** color **/ color(0, 0, 0, 200) /** endcolor **/;
        } else {
            // 50% of the time, give the particle a random color from within a predefined color palette
            int offset = 3 * int(random(0.0, (PALETTE.length - 1) / 3.0));
            
            _fill  = color(PALETTE[offset], 
                           PALETTE[offset + 1], 
                           PALETTE[offset + 2], 
                           /** int [ 0, 255 ] **/ 255 /** endint **/);
        }
    }
    
    private void _reset_length() {
        _length = int(random(/** int [ 5, 50 ]   **/ 10 /** endint **/, /** int [ 50, 300 ] **/ 100 /** endint **/));
    }
    
    boolean update() {
        // update particle direction and size
        _theta += _dTheta;
        _size  -= (_size / (MAX_TREE_SIZE * /** float [ 1, 128 ] **/ 16.0 /** endfloat **/));
        
        // kill particle if it grows too small
        if (_size <= MIN_TREE_SIZE) {
            return false;
        }
        
        // update particle's position
        _x += PARTICLE_SPEED * cos(_theta);
        _y += PARTICLE_SPEED * sin(_theta);
        
        float radius = _size / 2.0;
        
        // kill particle if it strays outside the canvas
        if (_x + radius < 0 || _x - radius >= width || 
            _y + radius < 0 || _y - radius >= height) {
            return false;
        }
        
        _length--;
        
        if (_length <= 0) {
            // spawn a new branch
            particles.add(Particle._spawn(this));
            
            _reset_length();
        } else {
            float rand = random(0.0, 1.0);
            
            if (rand < /** float [ 0, 0.1 ] **/ 0.005 /** endfloat **/) {
                // split into two branches and stop this particle's growth
                particles.add(Particle._spawn(this, true));
                particles.add(Particle._spawn(this, false));
                
                return false;
            } else if (rand > /** float [ 0.9, 1 ] **/ 0.99 /** endfloat **/) {
                // possible to change direction
                _dTheta = -_dTheta;
            }
        }
        
        return true;
    }
    
    void draw() {
        float radius = _size / 2.0;
        
        fill(_fill);
        stroke(/** color **/ color(127, 127, 127, 50) /** endcolor **/);
        strokeWeight(/** int [ 0, 10 ] **/ 1.0 /** endint **/);
        
        ellipse(_x, _y, radius, radius);
    }
}

/* RGB triples constituting a list of predefined colors
 * taken from "Images/shiftingLinesPalette.png"
 * (mainly blue and green hues)
 */
static int[] PALETTE = {
    59, 70, 76, 69, 88, 90, 75, 90, 91, 84, 93, 99, 83, 100, 99, 
    79, 104, 102, 84, 108, 116, 85, 112, 117, 94, 120, 107, 92, 115, 114, 
    98, 114, 114, 99, 122, 115, 104, 118, 121, 99, 122, 122, 99, 123, 130, 
    100, 124, 139, 104, 124, 147, 108, 131, 122, 106, 130, 117, 108, 130, 138, 
    109, 133, 136, 112, 141, 134, 116, 148, 145, 119, 153, 152, 117, 143, 170, 
    120, 143, 177, 125, 153, 188, 126, 154, 193, 129, 158, 200, 140, 171, 214, 
    145, 177, 219, 91, 114, 107, 107, 131, 136, 118, 144, 173, 120, 145, 174, 
    125, 152, 182, 141, 172, 215, 146, 177, 221, 59, 74, 77, 74, 86, 83, 
    83, 94, 105, 81, 99, 107, 79, 104, 111, 85, 102, 112, 89, 103, 112, 
    92, 117, 123, 97, 110, 121, 105, 125, 114, 106, 125, 156, 106, 131, 129, 
    107, 137, 132, 109, 138, 134, 113, 141, 139, 117, 146, 145, 120, 150, 150, 
    117, 142, 173, 124, 160, 158, 127, 160, 176, 130, 160, 197, 141, 174, 217, 
    149, 181, 225, 62, 76, 83, 76, 86, 92, 88, 94, 101, 78, 102, 112, 
    90, 108, 114, 95, 121, 102, 94, 120, 115, 106, 121, 123, 105, 123, 130, 
    107, 125, 137, 109, 138, 136, 117, 136, 138, 119, 142, 146, 120, 146, 151, 
    119, 142, 176, 128, 161, 178, 133, 162, 201, 75, 86, 96, 112, 126, 131, 
    112, 132, 120, 110, 134, 117, 113, 136, 137, 120, 135, 138, 120, 141, 146, 
    120, 145, 152, 120, 145, 177, 126, 162, 160, 151, 184, 227, 61, 80, 78, 
    75, 92, 86, 82, 99, 92, 94, 121, 123, 102, 128, 147, 108, 131, 144, 
    120, 136, 139, 120, 146, 146, 120, 153, 150, 120, 143, 180, 120, 145, 185, 
    125, 156, 191, 134, 166, 205, 148, 179, 222, 151, 183, 228, 61, 80, 83, 
    77, 99, 91, 78, 98, 99, 104, 118, 128, 102, 128, 150, 107, 131, 147, 
    117, 135, 142, 118, 147, 149, 118, 145, 180, 125, 158, 197, 129, 161, 200, 
    152, 183, 229, 85, 112, 103, 89, 109, 107, 96, 109, 101, 96, 109, 107, 
    84, 110, 129, 92, 117, 131, 99, 129, 124, 95, 128, 111, 103, 130, 154, 
    106, 130, 149, 112, 134, 147, 122, 156, 154, 117, 145, 163, 118, 146, 171, 
    126, 159, 200, 136, 165, 204, 153, 185, 229, 64, 78, 86, 83, 106, 99, 
    85, 109, 105, 85, 112, 107, 85, 112, 120, 97, 109, 114, 101, 128, 109, 
    112, 136, 124, 108, 131, 150, 112, 134, 152, 112, 138, 157, 113, 141, 158, 
    126, 160, 198, 149, 180, 223, 80, 86, 86, 80, 92, 86, 86, 113, 129, 
    109, 133, 161, 82, 87, 90, 81, 91, 90, 80, 96, 86, 90, 113, 102, 
    105, 128, 110, 101, 131, 129, 107, 130, 156, 109, 133, 152, 115, 139, 147, 
    111, 136, 160, 110, 134, 168, 120, 145, 171, 122, 149, 176, 127, 160, 201, 
    130, 162, 204, 134, 165, 208, 37, 45, 57, 0, 0, 0, 97, 116, 132, 
    98, 118, 139, 115, 139, 149, 110, 134, 167, 124, 150, 176, 127, 157, 193, 
    65, 79, 88, 89, 99, 100, 92, 116, 137, 101, 128, 114, 110, 136, 151, 
    113, 137, 153, 110, 136, 166, 124, 150, 173, 126, 152, 175, 128, 154, 181, 
    131, 160, 194, 135, 168, 210, 64, 80, 78, 89, 100, 105, 96, 114, 102, 
    100, 116, 122, 92, 120, 131, 110, 136, 154, 119, 141, 153, 113, 138, 162, 
    110, 136, 168, 117, 145, 177, 119, 149, 179, 128, 153, 186, 132, 159, 196, 
    136, 166, 209, 88, 101, 94, 119, 142, 151, 72, 86, 79, 70, 89, 96, 
    89, 105, 100, 97, 117, 107, 98, 121, 108, 93, 120, 139, 111, 144, 134, 
    112, 144, 133, 112, 134, 165, 128, 160, 159, 132, 164, 182, 138, 169, 210, 
    67, 84, 82, 97, 120, 102, 111, 144, 136, 112, 144, 137, 139, 170, 213, 
    88, 105, 94, 94, 122, 144, 99, 118, 145, 114, 145, 140, 112, 135, 169, 
    128, 163, 160, 133, 167, 185, 39, 48, 59, 65, 84, 89, 73, 92, 99, 
    99, 121, 146, 112, 132, 133, 115, 147, 144, 112, 137, 165, 122, 148, 182, 
    124, 150, 184, 134, 163, 199, 113, 129, 133, 128, 152, 192, 134, 163, 204, 
    39, 48, 60, 69, 89, 85, 75, 95, 104, 77, 100, 108, 104, 124, 109, 
    102, 123, 152, 113, 132, 138, 114, 139, 141, 118, 152, 149, 115, 144, 162, 
    114, 139, 171, 124, 150, 180, 129, 157, 195, 144, 175, 220,   
};

