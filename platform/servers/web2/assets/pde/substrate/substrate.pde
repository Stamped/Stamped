/*! substrate.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Recursive line particles.
 * 
 * Original concept and code by J. Tarbell
 * @see http://www.complexification.net/
 */

static int NUM_INITIAL_CRACKS   = /** int [ 1, 32 ]    **/ 4    /** endint   **/;
static int MAX_ACTIVE_CRACKS    = /** int [ 12, 1024 ] **/ 100  /** endint   **/;

static float CURVATURE          = /** float [ 0, 1 ]   **/ 0    /** endfloat **/;

static int SPAWN_TYPE           = /** int [ 0, 1 ]     **/ 0    /** endint   **/;
static int SPAWN_PERPENDICULAR  = 0;

static float FUZZ               = /** float [ 0, 4 ]   **/ 0.25 /** endfloat **/;
static float TWICE_FUZZ         = FUZZ * 2.0;

static int GROWTH_RATE_COEFF    = /** int [ 0, 10 ]    **/ 5    /** endint   **/;

int[][] _setCracks;
PImage  _offscreen;

ArrayList _activeCracks;
ArrayList _inactiveCracks;

boolean _dragged;

int _mouseDownX;
int _mouseDownY;

int _activeLength, _inactiveLength;

void setup() {
    size(/** int ( 0, 1024 ] **/ 640 /** endint **/, /** int ( 0, 1024 ] **/ 480 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 24 /** endint **/);
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    
    _setCracks      = new int[width + 1][height + 1];
    
    _activeCracks   = new ArrayList();
    _inactiveCracks = new ArrayList();
    
    _dragged        = false;
    
    _activeLength   = 0;
    _inactiveLength = 0;
    
    _offscreen      = createImage(width, height, RGB);
    
    for(int i = 0; i < width; i++) {
        for(int j = 0; j < height; j++) {
            _setCracks[i][j] = 1000;
            _offscreen.set(i, j, /** color **/ #FFFFFF /** endcolor **/);
        }
    }
    
    // create and initialize default cracks
    for(int i = 0; i < NUM_INITIAL_CRACKS; i++) {
        Crack newCrack = new Crack();
        
        _activeCracks.add(newCrack);
    }
}

void draw() {
    update();
    image(_offscreen, 0, 0);
    
    // if user is dragging mouse, show a preview-line
    if (_dragged) {
        float newX  = mouseX;
        float newY  = mouseY;
        
        // if shift is pressed, align preview-line to 90 degree increments
        if (keyCode == SHIFT) {
            int dx  = mouseX - _mouseDownX;
            int dy  = mouseY - _mouseDownY;
            
            float theta = getTheta(dx, dy);
            float dist  = sqrt(dx * dx + dy * dy);
            
            newX    = _mouseDownX + dist * cos(theta);
            newY    = _mouseDownY + dist * sin(theta);
        }
        
        // draw a variable-length line in direction new crack would go in
        stroke(color(0, 0, 0, 127));
        line(_mouseDownX, _mouseDownY, newX, newY);
    }
}

void update() {
    for (int i = 0; i < _activeCracks.size(); i++) {
        Crack cur = ((Crack) _activeCracks.get(i));
        int oldLength = cur.getLength();
        
        // update the position of the current crack and cleanup if it becomes inactive
        if (!cur.update()) {
            _activeLength -= cur.getLength();
            _activeCracks.remove(i);
            
            _inactiveLength += cur.getLength();
            _inactiveCracks.add(cur);
            
            boolean exp = true;
            
            for(int j = 0; j < GROWTH_RATE_COEFF; j++) {
                exp = (random(0.0, 1.0) > /** float [ 0, 1 ] **/ 0.5 /** endfloat **/);
                
                if (!exp) {
                    break;
                }
            }
            
            int stop = (exp ? 2 : 1);
            
            for(int k = 0; k < stop; k++) {
                Crack newCrack = spawnNewCrack();
                
                if (newCrack != null) {
                    _activeLength += newCrack.getLength();
                    _activeCracks.add(newCrack);
                }
            }
        } else {
            _activeLength += cur.getLength() - oldLength;
        }
    }
}

Crack spawnNewCrack() {
    if (_activeCracks.size() > MAX_ACTIVE_CRACKS) {
        return null;
    }
    
    int randomCrack = int(random(0, _activeLength + _inactiveLength - 1));
    int length = 0;
    
    if (randomCrack < _activeLength) {
        for (int i = 0; i < _activeCracks.size(); i++) {
            Crack cur = ((Crack) _activeCracks.get(i));
            
            length += cur.getLength();
            if (length > randomCrack) {
                return cur.spawnNewCrack(SPAWN_TYPE);
            }
        }
        
        return null;
    }
    
    randomCrack -= _activeLength;
    
    for (int i = 0; i < _inactiveCracks.size(); i++) {
        Crack cur = ((Crack) _inactiveCracks.get(i));
        
        length += cur.getLength();
        if (length > randomCrack) {
            return cur.spawnNewCrack(SPAWN_TYPE);
        }
    }
    
    return null;
}

float getTheta(int dx, int dy) {
    float theta = atan2(dy, dx);
    
    if (keyCode == SHIFT) {
        boolean top = (theta < 0);
        
        if (top) {
            theta = -theta;
        }
        
        if (theta < PI / 4) {
            theta = 0;
        } else if (theta < 3 * PI / 4 && !top) {
            theta = PI / 2;
        } else if (theta < 5 * PI / 4 && (!top || theta > 3 * PI / 4)) {
            theta = PI;
        } else if (theta < 7 * PI / 4) {
            theta = 3 * PI / 2;
        }
    }
    
    return theta;
}

void mousePressed() {
    _mouseDownX = mouseX;
    _mouseDownY = mouseY;
}

// Allow user to add Cracks at his/her discretion via mouse input
void mouseReleased() {
    if (_dragged) {
        _dragged = false;
        
        int x = mouseX, y = mouseY;
        int dx = x - _mouseDownX;
        int dy = y - _mouseDownY;
        
        int theta = (int)(180 * this.getTheta(dx, dy) / PI);
        this.addInputCrack(theta);
    }
}

void mouseClicked() {
    this.addInputCrack(random(0, 359));
}

void mouseDragged() {
    _dragged = true;
}

void addInputCrack(float theta) {
    _activeCracks.add(new Crack(_mouseDownX, _mouseDownY, theta));
}

class Crack {
    // position
    float _x, _initialX;
    float _y, _initialY;
    
    // direction specified in degrees
    int _theta;
    float _dx, _dy;
    
    float _sandRand, _scale, _radiusScale;
    boolean _curved;
    
    color _color;
    int _length;
    
    // initializes a completely randomized crack
    Crack() {
        this(random(0, width), random(0, height), random(0, 359));
    }
    
    // initializes a given crack with a random color
    Crack(float x, float y, float theta) {
        // initialize geometric data
        _initialX   = x;
        _initialY   = y;
        _x          = x;
        _y          = y;
        _length     = 0;
        
        _sandRand   = random(0.0, 0.1);
        _curved     = (CURVATURE > random(0.0, 1.0));
        
        if (_curved) {
            // make particle's path elliptical instead of circular
            _scale  = PI * random(0.0, 1.0) / 4.0;
            
            // make particle curve slowly/gradually
            _radiusScale = (PI / ((180 - 50 + int(random(0, 100))) << 3));
            _dx     = 0.4 * (1 - 2 * random(0.0, 1.0));
            _dy     = 0.4 * (1 - 2 * random(0.0, 1.0));
            _theta  = int(random(-2000000, -1000));
        } else { // crack is a line so it's velocity will be constant
            _theta     = (int(theta) + 2 - int(random(0, 4))) % 360;
            _dx        = (float)(0.42 * cos(_theta * (PI / 180)));
            _dy        = (float)(0.42 * sin(_theta * (PI / 180)));
        }
        
        // initialize crack to have a pseudo-random color within the predefined color scheme
        int offset = 3 * int(random(0, (PALETTE.length - 1) / 3));
        _color = color(PALETTE[offset], 
                       PALETTE[offset + 1], 
                       PALETTE[offset + 2], 
                       /** int [ 0, 255 ] **/ 255 /** endint **/);
    }
    
    boolean update() {
        float dX = _dx, dY = _dy;
        
        // update velocity of curved particles
        if (_curved) {
            // _length acts as time
            float angle = _length * _radiusScale;
            
            dX = _dx * sin(angle + _scale);
        }
        
        // update particle's position
        _x += dX;
        _y += dY;

        int realX = round(_x), realY = round(_y);
        
        // make line "fuzzy" to prevent the uniform aliases which are otherwise produced
        int x = (int)(_x + FUZZ - random(0.0, 1.0) * TWICE_FUZZ);
        int y = (int)(_y + FUZZ - random(0.0, 1.0) * TWICE_FUZZ);
        
        // check if it's time for this particle to die
        if (!this.isValid(x, y, _length) || !this.isValid(realX, realY, _length++)) {
            return false;
        }
        
        this.paintSand(x, y, dX, dY);
        _setCracks[x][y] = _theta;
        
        _offscreen.set(x, y, /** color **/ #000000 /** endcolor **/);
        _setCracks[realX][realY] = _theta;
        
        return true;
    }
    
    // blends a src ARGB pixel onto a destination RGB pixel
    void setPixel(int x, int y, color c) {
        color oldColor = _offscreen.get(x, y);
        int a = int(alpha(c));
        
        // blend the two colors together, weighting their relative contributions
        // according to the new color's alpha value
        int k = (255 - a);
        int r = cap(int((a * red(c)   + k * red(oldColor))   / 255));
        int g = cap(int((a * green(c) + k * green(oldColor)) / 255));
        int b = cap(int((a * blue(c)  + k * blue(oldColor))  / 255));
        
        _offscreen.set(x, y, color(r, g, b, 255));
    }
    
    void paintSand(int oldX, int oldY, float dX, float dY) {
        float sandX  = oldX,   sandY  = oldY;
        float sandDx = dY / 2, sandDy = dX / 2;
        int length = -3;
        
        do {
            // sand moves perpendicular to Crack
            sandX += sandDx;
            sandY -= sandDy;
        } while(isValid((int) sandX, (int) sandY, length++));
        
        sandX = (sandX - sandDx - _x);
        sandY = (sandY + sandDy - _y);
        
        // modulate length of sand
        float sand_const = /** float [ 1, 100 ] **/ 50 /** endfloat **/;
        float modulation = 0.01 + (abs(sandX)) * (1.0 / (sand_const * width)) + 
                                  (abs(sandY)) * (1.0 / (sand_const * height));
        
        _sandRand += modulation - random(0.0, 1.0) * modulation * /** float [ 0.1, 10 ] **/ 2 /** endfloat **/;
        
        // cap length of sand
        if (_sandRand < 0.3) {
            _sandRand = 0.3;
        }
        
        if (_sandRand > 1) {
            _sandRand = 1;
        }
        
        int noGrains = 128;
        
        // draw sand (pixels w/ varying levels of transparency)
        float wAdd = _sandRand / (noGrains - 1);
        float w    = 0;
        
        float startX = _x + 0.15 - random(0.0, 1.0) * 0.3;
        float startY = _y + 0.15 - random(0.0, 1.0) * 0.3;
        float denom  = noGrains;
        
        for(int i = 0; i < noGrains; i++, w += wAdd) {
            float sinSinW = sin(sin(w));
            int x = round(startX + sandX * sinSinW);
            int y = round(startY + sandY * sinSinW);
            
            if (x != oldX || y != oldY) {
                int a = cap(int((16 * (noGrains - i) / denom)));
                
                if (x > 0 && y > 0 && x < width && y < height) {
                    this.setPixel(x, y, color(red(_color), green(_color), blue(_color), a));
                }
                
                oldX = x;
                oldY = y;
            }
        }
    }
 
    int cap(int c) {
        return (c >= 255 ? 255 : (c <= 0 ? 0 : c));
    }
    
    boolean isValid(int x, int y, int length) {
        return (x > 0 && x < width  - 1 && 
                y > 0 && y < height - 1 &&  
                (length <= 1 || _setCracks[x][y] > 361 || _setCracks[x][y] == _theta));
    }
    
    Crack spawnNewCrack(int spawnType) {
        boolean randBoolean = (random(0.0, 1.0) > 0.5);
        int newTheta = _theta;
        
        float newX = _initialX, newY = _initialY;
        if (_curved) {
            int t = int(random(0, _length));
            
            float angle = 0;
            for(int i = 0; i < t; i++, angle += _radiusScale) {
                
                newX += _dx * cos(angle);
                newY += _dy * sin(angle + _scale);
            }
            
            // get angle of curve's tangent vector at spawn point
            newTheta = (int)(angle * (180 / PI));
        } else {
            float t = (random(0.0, 1.0) * _length);
            
            newX += t * _dx;
            newY += t * _dy;
        }
        
        if (spawnType == SPAWN_PERPENDICULAR) {
            newTheta += (randBoolean ? 90 : 270);
        } else {
            newTheta += (randBoolean ? random(5, 174) : random(185, 354));
        }
        
        return new Crack(newX, newY, newTheta);
    }
    
    int getLength() {
        return _length;
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

