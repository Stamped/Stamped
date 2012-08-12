/*! primordial.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing
 */

static int SIMULATION_WIDTH     = /** int ( 0, 1024 ] **/ 640 /** endint **/;
static int SIMULATION_HEIGHT    = /** int ( 0, 1024 ] **/ 480 /** endint **/;

static int NUM_ORGANISMS        = /** int [ 1, 100 ]  **/ 15  /** endint **/;
static int MAX_NUM_OCTOPI       = /** int [ 0, 100 ]  **/ 3   /** endint **/;

Particle[] _particles;

boolean _singleCelled;
boolean _flagella;
boolean _octopi;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(/** int [ 1, 60 ] **/ 24 /** endint **/);
    loop();
    
    _singleCelled = /** boolean **/ false /** endboolean **/;
    _flagella     = /** boolean **/ true  /** endboolean **/;
    _octopi       = /** boolean **/ true  /** endboolean **/;
    
    reset();
}

void reset() {
    Particle[] particles   = new Particle[NUM_ORGANISMS];
    
    // ugly, but it works for the purposes of this simulation
    int chanceOfSingle     = 18;
    int chanceOfFlagellum  = 92  - chanceOfSingle;
    int chanceOfOctopus    = 100 - chanceOfFlagellum;
    
    if (!_singleCelled) {
        chanceOfSingle     = -1000;
        chanceOfFlagellum += 9;
        chanceOfOctopus   += 9;
    }
    
    if (!_flagella) {
        chanceOfFlagellum  = -1000;
        chanceOfSingle    += 64;
        chanceOfOctopus   += 10;
    }
    
    if (!_octopi) {
        chanceOfOctopus    = -1000;
        chanceOfSingle    += 3;
        chanceOfFlagellum += 7; 
    }
    
    if (chanceOfSingle < 0) {
        chanceOfSingle = 0;
    }
    
    if (chanceOfFlagellum < 0) {
        chanceOfFlagellum = 0;
    }
    
    if (chanceOfOctopus < 0) {
        chanceOfOctopus = 0;
    }
    
    chanceOfFlagellum += chanceOfSingle;
    chanceOfOctopus   += chanceOfFlagellum;
    
    int noOctopi = 0;
    
    for(int i = 0; i < particles.length; i++) {
        boolean is_octopus = false;
        float rand = random(0, 99);
        Particle o = null;
        
        float x = random(width);
        float y = random(height);
        //float x = width  / 2.0;
        //float y = height / 2.0;
        
        //o = new Cell(x, y);
        //o = new Flagellum(x, y);
        //o = new Octopus(x, y);
        
        if (rand < chanceOfSingle) {
            o = new Cell(x, y);
        } else if (rand < chanceOfFlagellum) {
            o = new Flagellum(x, y);
        } else if (rand < chanceOfOctopus) {
            o = new Octopus(x, y);
            is_octopus = true;
        } else if (_flagella) {
            o = new Flagellum(x, y);
        } else {
            boolean rand2 = (_singleCelled && _octopi) ? (random(0.0, 1.0) > 0.5) : true;
            
            if (_singleCelled && rand2) {
                o = new Cell(x, y);
            } else if (_octopi && rand2) {
                o = new Octopus(x, y);
                is_octopus = true;
            }
        }
        
        if (o != null && is_octopus && ++noOctopi > MAX_NUM_OCTOPI) {
            o = null;
        }
        
        particles[i] = o;
    }
    
    _particles = particles;
}

void draw() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    update();
    
    for(int i = 0; i < _particles.length; i++) {
        if (_particles[i] != null) {
            _particles[i].draw();
        }
    }
}

void update() {
    for(int i = 0; i < _particles.length; i++) {
        if (_particles[i] != null) {
            _particles[i].update();
        }
    }
}

void mouseClicked() {
    reset();
}

interface Particle {
    boolean update();
    void    draw();
}

class Cell implements Particle {
    // position of center of cell
    float _x, _y;
    
    // physical attributes of cell that affect behavior
    float _size, _girth;
    
    // direction specified in radians
    float _theta;
    
    // speed of cell in current direction
    float _speed;
    
    // friction with water
    float _viscosity;
    
    // the velocity at which the cell is currently turning (modifies _theta)
    float _rotationalVelocity;
    
    // constraints placed on the turning velocity of the cell
    float _minRotationalVelocity, _maxRotationalVelocity;
    
    // constraints placed on the speed of the cell
    float _minSpeed, _maxSpeed;
    
    color _fill;
    
    Cell(float x, float y) {
        this(x, y, random(8, 50));
    }
    
    Cell(float x, float y, float size) {
        this(x, y, size, 0);
    }
    
    Cell(float x, float y, float size, float girth) {
        _x     = x;
        _y     = y;
        _size  = size / 2;
        _girth = girth;
        
        // viscosity = friction with water
        float viscosity_base = /** float [ 0, 10 ] **/ 0.9 /** endfloat **/;
        float viscosity_rand = /** float [ 0, 2  ] **/ 0.1 /** endfloat **/;
        
        _viscosity = viscosity_base + random(0.0, viscosity_rand);
        
        _minRotationalVelocity = /** float [ -0.1, 0 ] **/ -0.06 /** endfloat **/;
        _maxRotationalVelocity = /** float [ 0, 0.1  ] **/  0.06 /** endfloat **/;
        
        _minSpeed = /** float [ 0, 5 ]  **/ 2  /** endfloat **/;
        _maxSpeed = /** float [ 5, 25 ] **/ 10 /** endfloat **/;
        
        _speed = 0;//random(_minSpeed, _maxSpeed);
        _theta = random(0.0, TWO_PI);
        
        _fill  = /** color **/ color(127, 127, 127, 58) /** endcolor **/;
    }
    
    boolean update() {
        // randomly update speed of organism
        _speed += 0.03 - 0.06 * random(0.0, 1.0);
        
        // ensure organism doesn't move too fast
        _speed = this.cap(_speed, _minSpeed, _maxSpeed);
        
        float constant = /** float [ 0, 0.08 ] **/ 0.015 /** endfloat **/;
        
        // randomly update direction of organism
        _rotationalVelocity += constant - 2 * constant * random(0.0, 1.0);
        
        // ensure organism doesn't turn too fast
        _rotationalVelocity = this.cap(_rotationalVelocity, _minRotationalVelocity, 
                                       _maxRotationalVelocity);
        
        // organism will swim around randomly
        _theta += _rotationalVelocity;
        _rotationalVelocity *= _viscosity; // friction with water
        
        // update organism's position (determined by its 'head')
        float x = _x + (_speed * cos(_theta)); 
        float y = _y + (_speed * sin(_theta));
        
        setLocation(x, y);
        return true;
    }
    
    void setLocation(float x, float y) {
        _x = x;
        _y = y;
    }
    
    float cap(float value, float min, float max) {
        if (value < min) {
            value = min;
        } else if (value > max) {
            value = max;
        }
        
        return value;
    }
    
    float getSize() {
        return _size;
    }
    
    void setSize(float size) {
        _size = size / 2;
    }
    
    float getGirth() {
        return _girth;
    }
    
    void setGirth(float girth) {
        _girth = girth;
    }
    
    void setRotationalBounds(float min, float max) {
        _minRotationalVelocity = min;
        _maxRotationalVelocity = max;
    }
    
    void setSpeedBounds(int length) {
        _minSpeed = 1 + (length - 16) * 0.2;
        _maxSpeed = 7 - (35 - length) * 0.2;
    }
    
    void setFill(color c) {
        _fill = c;
    }
    
    void draw() {
        fill(_fill);
        strokeWeight(/** float [ 0, 10 ] **/ 0 /** endfloat **/);
        stroke(/** color **/ color(255, 255, 255, 0) /** endcolor **/);
        
        float x = _x;
        float y = _y;
        
        // wrap display coordinates
        if (x < -_size) {
            x = width  + _size - ((-x) % (width  + _size * 2));
        } else {
            x = x % (width + _size);
        }
        
        if (y < -_size) {
            y = height + _size - ((-y) % (height + _size * 2));
        } else {
            y = y % (height + _size);
        }
        
        ellipse(x, y, _size, _size);
    }
}

class Flagellum implements Particle {
    // makes the flagellum rhythmically undulate
    float _muscularFrequency, _noMuscles, _muscleRange;
    
    // body of the flagellum
    Cell[] _cells;
    
    // head cell which dictates the flagellum's movement
    Cell _head;
    
    Flagellum(float x, float y) {
        this(x, y, int(random(12, 35)));
    }
    
    Flagellum(float x, float y, int length) {
        this(x, y, length, 1.65 + 0.8 * random(0.0, 1.0), null);
    }
    
    Flagellum(float x, float y, int length, float connectedness, Cell head) {
        // How often organism will undulate
        _muscularFrequency = 0.1 + 0.4 * random(0.0, 1.0);
        _noMuscles = 0;
        
        // How prevalent the undulation will be (greater = more undulation)
        _muscleRange = ((8 - random(0, 16)) * PI / 180);
        
        length += int(random(-3, 3));
        
        // bound length to within bounds empirically chosen to be reasonable
        if (length < 12) {
            length = 12;
        } else if (length > 35) {
            length = 35;
        }
        
        _cells = new Cell[length];
        
        float size = (length * length) / 16.0;
        Cell h = new Cell(x, y, size);
        h.setSpeedBounds(length);
        _head = h;
        
        _cells[0] = head;
        
        if (head != null) {
            _cells[0] = head;
        } else {
            _cells[0] = _head;
        }
        
        for(int i = 1; i < _cells.length; i++) {
            int j = (_cells.length - i);
            size  = (j * j) / 16.0;
            
            // smaller girth = more compact particles
            // larger girth  = more loosely connected particles
            float girth = size * connectedness / (j * 0.2);
            
            _cells[i] = new Cell(x, y, size, girth);
        }
        
        // make head of organism light purple
        _cells[1].setFill(/** color **/ color(164, 0, 164, 18) /** endcolor **/);
    }
    
    boolean update() {
        if (_cells[0] == _head) {
            _head.update();
        }
        
        // randomly pulse 2nd 'muscle' node
        _noMuscles += _muscularFrequency;
        float muscleTheta = _head._theta + _muscleRange * sin(_noMuscles);
        
        // make 2nd 'muscle' node follow head node
        _cells[1]._x = _cells[0]._x - (_cells[0].getSize() / 2.0 * cos(muscleTheta));
        _cells[1]._y = _cells[0]._y - (_cells[0].getSize() / 2.0 * sin(muscleTheta));
        
        // apply kinetic forces throughout body
        for(int i = 2; i < _cells.length; i++) {
            float dx = _cells[i]._x - _cells[i - 2]._x;
            float dy = _cells[i]._y - _cells[i - 2]._y;
            
            float dist  = sqrt(dx * dx + dy * dy);
            float girth = _cells[i].getGirth();
            
            _cells[i].setLocation(_cells[i - 1]._x + (dx * girth) / dist, 
                                  _cells[i - 1]._y + (dy * girth) / dist);
        }
        
        return true;
    }
    
    void draw() {
        for(int i = 1; i < _cells.length; i++) {
            _cells[i].draw();
        }
    }
}

class Octopus implements Particle {
    // tentacles attached to head cell
    Flagellum[] _flagella;
    
    // hidden cell which controls this Octopus' movement
    Cell _head;
    
    Octopus(float x, float y) {
        // average length of tentacles (number of cells in a flagellum)
        int length = int(random(12, 30));
        
        // diameter of octopus' head
        float size = (length * length) / 16;
        
        // initialize the head / root cell
        _head = new Cell(x, y, size);
        _head.setSpeedBounds(length);
        _head.setFill(/** color **/ color(164, 0, 164, 48) /** endcolor **/);
        
        // create and initialize all of the tentacles
        _flagella = new Flagellum[int(random(7, 24))];
        
        float connectedness = 1.2 + 0.5 * random(0.0, 1.0);
        
        for(int i = 0; i < _flagella.length; i++) {
            _flagella[i] = new Flagellum(x, y, length, connectedness, _head);
        }
    }
    
    boolean update() {
        // update position and orientation of head cell
        _head.update();
        
        // update body tentacles to follow suit
        for(int i = 0; i < _flagella.length; i++) {
            _flagella[i].update();
        }
        
        return true;
    }
    
    void draw() {
        _head.draw();
        
        for(int i = 0; i < _flagella.length; i++) {
            _flagella[i].draw();
        }
    }
}

