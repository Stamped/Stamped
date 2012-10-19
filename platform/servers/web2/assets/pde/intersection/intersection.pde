/*! intersection.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 * 
 * Original concept by Casey Reas (http://reas.com/)
 * 
 * A surface filled with 100 medium to small sized circles.
 * Each circle has a different size and direction, but moves 
 * at the same slow rate. Display:
 *  A. The instantaneous intersections of the circles.
 *  B. The aggregate intersections of the circles.
 * 
 * @see http://reas.com/iperimage.php?section=works&work=preprocess_s&images=4&id=1&bgcolor=FFFFFF
 * @see http://www.complexification.net/gallery/machines/interAggregate/index.php
 */

static int VARIATION            = /** int [ 0, 2 ]    **/ 0    /** endint     **/;
static int NUM_CIRCLES          = /** int [ 1, 200 ]  **/ 100  /** endint     **/;
static int CIRCLE_MOVEMENT      = /** int [ 0, 2 ]    **/ 0    /** endint     **/;

static int CIRCLE_RADIUS        = /** int [ 10, 70 ]  **/ 30   /** endint     **/;
static int MIN_CIRCLE_RADIUS    = /** int [ 0, 70 ]   **/ 10   /** endint     **/;
static int MAX_CIRCLE_RADIUS    = /** int [ 10, 140 ] **/ 70   /** endint     **/;
static boolean RANDOM_RADIUS    = /** boolean         **/ true /** endboolean **/;

Circle[] _circles;

void setup() {
    size(/** int ( 0, 1024 ] **/ 640 /** endint **/, /** int ( 0, 1024 ] **/ 480 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 30 /** endint **/);
    loop();
    
    reset();
}

void reset() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    
    Circle[] circles = new Circle[NUM_CIRCLES];
    
    for(int i = 0; i < circles.length; i++) {
        int x = int(random(0, width  - 1));
        int y = int(random(0, height - 1));
        int radius = CIRCLE_RADIUS;
        
        if (RANDOM_RADIUS) {
            radius = int(random(MIN_CIRCLE_RADIUS, MAX_CIRCLE_RADIUS));
        }
        
        int offset = 3 * int(random(0, (PALETTE.length - 1) / 3));
        color c = color(PALETTE[offset], 
                        PALETTE[offset + 1], 
                        PALETTE[offset + 2], 
                        /** int [ 0, 255 ] **/ 48 /** endint **/);
        
        circles[i] = new Circle(x, y, radius, c);
    }
    
    _circles = circles;
}

void draw() {
    if (VARIATION == 2) {
        background(/** color **/ #FFFFFF /** endcolor **/);
    }
    
    update();
    
    if (VARIATION == 2) {
        stroke(/** color **/ #666666 /** endcolor **/);
        fill  (/** color **/ color(0, 0, 0, 24) /** endcolor **/);
        
        for(int i = 0; i < _circles.length; i++) {
            _circles[i].draw();
        }
        
        stroke(/** color **/ #000000 /** endcolor **/);
        fill  (/** color **/ #000000 /** endcolor **/);
        
        int size = 4;
        
        // draw the intersections between all circles
        for(int i = 0; i < _circles.length - 1; i++) {
            for(int j = i + 1; j < _circles.length; j++) {
                PVector[] intersections = _circles[i].getIntersection(_circles[j]);
                
                if (intersections != null) {
                    // draw a line connecting the two points of intersection
                    if (intersections.length == 2) {
                        line(intersections[0].x, 
                             intersections[0].y, 
                             intersections[1].x, 
                             intersections[1].y);
                    }
                    
                    // draw the actual point(s) of intersection
                    for(int a = 0; a < intersections.length; a++) {
                        ellipse(intersections[0].x, intersections[0].y, 
                                size, size);
                    }
                }
            }
        }
    }
}

void update() {
    for(int i = 0; i < _circles.length; i++) {
        _circles[i].update();
    }
    
    if (VARIATION != 2) {
        // O(N^2)  TODO:  optimize to O(NlogN)
        for(int i = 0; i < _circles.length - 1; i++) {
            int diameter = _circles[i].getDiameter();
            
            for(int j = i + 1; j < _circles.length; j++) {
                color c = _circles[i].getColor();
                
                if (VARIATION != 1) {
                    PVector[] intersections = _circles[i].getIntersection(_circles[j]);
                    
                    if (intersections != null && intersections.length == 2) {
                        float difX      = intersections[1].x - intersections[0].x;
                        float difY      = intersections[1].y - intersections[0].y;
                        int distance    = int(sqrt(difX * difX + difY * difY));
                        int diameter2   = _circles[j].getDiameter(); 
                        
                        // want the smaller of the two diameters
                        int d = (diameter > diameter2 ? diameter2 : diameter);
                        
                        int a;
                        if (VARIATION == 0) {
                            a = 32 - ((distance << 5) / d);
                        } else {
                            a = 128 - (int)((distance << 8) / d);
                        }
                        
                        if (a > 255) {
                            a = 255;
                        } else if (a < 0) {
                            a = 255 + a;
                        }
                        
                        if (VARIATION == 0) {
                            c = color(red(c), green(c), blue(c), a);
                        } else {
                            c = color(red(c), green(c), blue(c), 24);
                        }
                        
                        // draw a line between the two points of intersection
                        stroke(c);
                        line(intersections[0].x, 
                             intersections[0].y, 
                             intersections[1].x, 
                             intersections[1].y);
                    }
                } else if (_circles[i].intersects(_circles[j])) {
                    // draw a line connecting the centers of the two 
                    // intersecting circles (VARIATION == 1)
                    stroke(c);
                    
                    line(_circles[i].getX(), 
                         _circles[i].getY(), 
                         _circles[j].getX(), 
                         _circles[j].getY());
                }
            }
        }
    }
}

void mouseClicked() {
    reset();
}
class Circle {
    int _radius, _radiusSquared, _diameter;
    
    float _x, _y;
    float _dX, _dY;
    
    color _color;
    
    Circle() {
        this(int(random(MIN_CIRCLE_RADIUS, MAX_CIRCLE_RADIUS)));
    }
    
    Circle(int radius) {
        this(int(random(0, width - 1)), int(random(0, height - 1)), radius);
    }
    
    Circle(int x, int y, int radius) {
        this(x, y, radius, color(255, 255, 255, 18), 0);
    }
    
    Circle(int x, int y, int radius, color c) {
        _x = x;
        _y = y;
        _color = c;
        
        this.setRadius(radius);
        this.setMovement(CIRCLE_MOVEMENT);
    }
    
    void setRadius(int radius) {
        _radius   = radius;
        _radiusSquared = radius * radius;
        _diameter = radius << 1;
    }
    
    void setMovement(int movement) {
        _dX = 0;
        _dY = 0;
        
        if (movement != 2) {
            _dX = 0.5 + random(0.0, 1.0);
            _dX *= (random(0.0, 1.0) > 0.5 ? 1 : -1);
        }
        
        if (movement != 1) {
            _dY = 0.5 + random(0.0, 1.0);
            _dY *= (random(0.0, 1.0) > 0.5 ? 1 : -1);
        }
    }
    
    void update() {
        int rand = int(random(0, 2));
        
        _x += _dX;
        _y += _dY;
        
        // wrap circle around the edge of the simulation
        if (_x + _radius < 0 && _dX < 0) {
            _x = width + _radius + rand;
        } else if (_x - _radius >= width && _dX > 0) {
            _x = -_radius - rand;
        }
        
        if (_y + _radius < 0 && _dY < 0) {
            _y = height + _radius + rand;
        } else if (_y - _radius >= height && _dY > 0) {
            _y = -_radius - rand;
        }
    }
    
    // accessors for instance vars
    float getX()            { return _x; }
    float getY()            { return _y; }
    int getRadius()         { return _radius; }
    int getRadiusSquared()  { return _radiusSquared; }
    int getDiameter()       { return _diameter; }
    color getColor()        { return _color; }
    
    boolean intersects(Circle circle) {
        int rad    = circle.getRadius();
        float xDif = circle.getX() - _x;
        float yDif = circle.getY() - _y;
        float d    = sqrt(xDif * xDif + yDif * yDif);
        
        // reject if distance btwn circles is greater than their radii combined
        if (d > _radius + rad) {
            return false;
        }
        
        // reject if one circle is inside of the other
        return (d >= abs(rad - _radius));
    }
    
    PVector[] getIntersection(Circle circle) {
        int rad     = circle.getRadius();
        float cirX  = circle.getX();
        float cirY  = circle.getY();
        float xDif  = cirX - _x;
        float yDif  = cirY - _y;
        float dist2 = xDif * xDif + yDif * yDif;
        float d     = sqrt(dist2);
        
        // reject if distance btwn circles is greater than their radii combined
        if (d > _radius + rad) {
            return null;
        }
        
        // reject if one circle is inside of the other
        if (d < abs(rad - _radius)) {
            return null;
        }
        
        xDif /= d;
        yDif /= d;
        
        // distance from this circle to line cutting through intersections
        float a = (_radiusSquared - circle.getRadiusSquared() + dist2) / (2 * d);
        
        // coordinates of midpoint of intersection
        float pX = _x + a * xDif; 
        float pY = _y + a * yDif;
        
        // the distance from (x, y) to either of the intersection points
        float h = sqrt(_radiusSquared - a * a);
        
        // check if there's only one intersection
        if (h == 0) {
            return new PVector[] { new PVector((int)pX, (int)pY) };
        }
        
        xDif *= h;
        yDif *= h;
        
        float x1 = (pX + yDif);
        float y1 = (pY - xDif);
        float x2 = (pX - yDif);
        float y2 = (pY + xDif);
       
        // there are (at least) two intersections
        return new PVector[] { new PVector(x1, y1), new PVector(x2, y2) };
    }
    
    void draw() {
        ellipse(_x, _y, _diameter, _diameter);
    }
}

// color palette extracted from a seed image
static int PALETTE[] = {
    255,255,255, 255,255,255, 255,255,255, 
    37, 29, 23, 51, 45, 39, 57, 49, 41, 71, 57, 42, 90, 74, 52, 
    100, 76, 55, 90, 85, 73, 104, 97, 77, 116, 104, 88, 123, 122, 119, 
    132, 120, 106, 147, 121, 83, 140, 129, 107, 161, 141, 117, 154, 139, 119, 
    141, 144, 139, 154, 148, 141, 176, 158, 146, 182, 168, 141, 187, 176, 140, 
    187, 179, 157, 189, 184, 165, 195, 184, 170, 202, 190, 173, 218, 209, 188, 
    213, 211, 196, 211, 218, 202, 220, 220, 219, 221, 221, 224, 43, 36, 25, 
    117, 108, 101, 137, 119, 89, 171, 158, 146, 181, 168, 145, 186, 179, 163, 
    220, 205, 186, 48, 31, 15, 48, 30, 20, 49, 46, 49, 58, 56, 52, 
    69, 59, 53, 102, 83, 46, 92, 90, 88, 99, 98, 88, 109, 112, 107, 
    125, 125, 129, 128, 110, 98, 133, 125, 119, 141, 137, 120, 167, 147, 109, 
    141, 145, 146, 153, 150, 149, 163, 158, 161, 179, 170, 155, 186, 180, 171, 
    189, 184, 173, 195, 188, 181, 204, 190, 178, 226, 196, 172, 220, 211, 195, 
    221, 217, 212, 222, 224, 221, 81, 62, 43, 102, 86, 56, 117, 100, 75, 
    126, 128, 123, 169, 152, 118, 147, 141, 135, 163, 158, 171, 170, 166, 163, 
    172, 169, 162, 183, 180, 177, 187, 183, 178, 211, 193, 172, 226, 204, 181, 
    217, 211, 203, 94, 96, 93, 150, 145, 123, 163, 159, 176, 167, 163, 169, 
    208, 189, 168, 223, 207, 196, 222, 225, 226, 34, 30, 32, 42, 40, 38, 
    80, 59, 49, 113, 79, 57, 122, 114, 102, 125, 128, 129, 145, 125, 106, 
    153, 137, 108, 177, 150, 106, 147, 141, 144, 169, 160, 141, 171, 171, 176, 
    187, 188, 187, 208, 189, 178, 211, 197, 181, 226, 210, 186, 225, 212, 195, 
    69, 64, 55, 114, 86, 58, 125, 113, 82, 172, 173, 174, 189, 192, 190, 
    202, 189, 184, 211, 196, 185, 232, 213, 186, 220, 216, 202, 42, 33, 13, 
    61, 61, 65, 67, 62, 65, 98, 79, 65, 124, 113, 74, 129, 101, 73, 
    131, 101, 60, 181, 154, 119, 165, 155, 145, 174, 176, 173, 194, 189, 193, 
    204, 196, 187, 242, 217, 186, 230, 216, 196, 226, 218, 203, 62, 64, 45, 
    73, 65, 40, 109, 97, 60, 135, 112, 61, 158, 146, 109, 173, 160, 118, 
    166, 163, 153, 196, 193, 158, 203, 195, 170, 212, 205, 196, 211, 211, 211, 
    226, 219, 212, 53, 40, 25, 83, 69, 26, 158, 160, 155, 196, 194, 142, 
    202, 199, 197, 206, 205, 205, 226, 222, 216, 52, 35, 11, 61, 64, 61, 
    118, 98, 60, 102, 87, 73, 105, 102, 101, 128, 93, 71, 148, 116, 76, 
    161, 125, 81, 177, 157, 134, 157, 156, 161, 158, 160, 160, 177, 172, 163, 
    190, 169, 142, 193, 170, 140, 205, 195, 159, 205, 205, 208, 213, 214, 216, 
    226, 222, 225, 92, 80, 56, 163, 141, 103, 178, 172, 169, 190, 170, 147, 
    211, 197, 156, 62, 65, 66, 76, 74, 69, 108, 109, 113, 166, 135, 77, 
    180, 161, 107, 178, 174, 177, 187, 172, 155, 194, 174, 151, 212, 200, 168, 
    206, 208, 203, 214, 216, 212, 233, 225, 204, 56, 48, 29, 66, 46, 35, 
    77, 77, 80, 101, 92, 86, 133, 109, 86, 168, 139, 90, 184, 162, 122, 
    179, 176, 165, 194, 177, 144, 196, 178, 141, 204, 196, 180, 205, 208, 208, 
    214, 216, 216, 231, 225, 216, 65, 44, 28, 84, 67, 41, 72, 52, 28, 
    77, 80, 76, 109, 113, 114, 134, 116, 72, 140, 129, 77, 174, 145, 94, 
    192, 159, 124, 160, 142, 131, 166, 154, 137, 180, 178, 172, 194, 179, 156, 
    212, 209, 203, 217, 213, 211, 234, 223, 205, 240, 227, 204, 140, 129, 87, 
    176, 145, 93, 193, 166, 121, 202, 182, 150, 211, 205, 204, 235, 225, 212, 
    241, 229, 212, 44, 45, 49, 84, 54, 30, 89, 80, 39, 84, 76, 68, 
    77, 81, 82, 179, 143, 92, 182, 184, 172, 206, 184, 147, 211, 185, 143, 
    211, 206, 209, 218, 214, 217, 236, 227, 218, 242, 235, 220, 45, 48, 45, 
    103, 93, 96, 147, 130, 79, 178, 163, 140, 205, 185, 155, 210, 187, 153, 
    211, 202, 186, 237, 232, 219, 139, 137, 135, 201, 182, 158, 212, 202, 182, 
    45, 49, 50, 64, 44, 53, 98, 73, 45, 82, 78, 80, 119, 94, 100, 
    150, 131, 85, 140, 140, 145, 187, 174, 164, 193, 174, 165, 217, 208, 175, 
    215, 208, 183, 229, 228, 226, 233, 231, 229,   
};

