/*! not_found.pde
 *  
 * @author: Travis Fischer
 * @date:   August 2012
 * 
 * @see: http://en.wikipedia.org/wiki/Rapidly_exploring_random_tree
 */

/* @pjs preload="/assets/pde/not_found/404.png"; */

static int   NUM_VERTICES = /** int   [ 1, 128 ] **/ 24   /** endint   **/;
static float CURVATURE    = /** float [ 0, 10  ] **/ 2.2  /** endfloat **/;
static float INV_DISTANCE = /** float [ 5, 200 ] **/ 40.0 /** endfloat **/;

static int MASK_THRESHOLD = /** int   [ 0, 255 ] **/ 5    /** endint   **/;

float _distance;
RRTree _tree;

PImage _offscreen;
PImage _mask;

ArrayList _masked;

void setup() {
    size(/** int ( 0, 1024 ] **/ 400 /** endint **/, /** int ( 0, 1024 ] **/ 350 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 60 /** endint **/);
    smooth();
    loop();
    
    String mask_path;
    
    if (online) {
        mask_path = "/assets/pde/not_found/404.png";
    } else {
        mask_path = "404.png";
    }
    
    _mask = loadImage(mask_path);
    
    if (_mask.width != width || _mask.height != height) {
        _mask.resize(width, height);
    }
    
    _masked = new ArrayList();
    
    for (int i = 0; i < _mask.height; i++) {
        for (int j = 0; j < _mask.width; j++) {
            if (is_masked(j, i)) {
                _masked.add(new PVector(j, i));
            }
        }
    }
    
    reset();
}

void reset() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    
    _offscreen = new PImage(width, height);
    
    _distance  = (width + height) / (2.0 * INV_DISTANCE);
    _tree = new RRTree();
}

void draw() {
    _tree.update();
}

void mouseClicked() {
    reset();
}

boolean is_masked(int x, int y) {
    if (x < 0 || x >= width || y < 0 || y >= height) {
        return false;
    } else {
        color c = _mask.get(x, y);
        
        return (red(c) < MASK_THRESHOLD);
    }
}

PVector get_vertex() {
    int i = int(random(0, _masked.size() - 1));
    
    return (PVector) _masked.get(i);
}

class RRTree {
    ArrayList _vertices;
    
    RRTree() {
        this(NUM_VERTICES);
    }
    
    RRTree(int num_vertices) {
        _vertices = new ArrayList(num_vertices);
        
        for (int i = 0; i < num_vertices; i++) {
            _vertices.add(get_vertex());
        }
    }
    
    color random_color(int a) {
        if (random(0.0, 1.0) > /** float [ 0, 1 ] **/ 0.0 /** endfloat **/) {
            // select a random color from within a predefined color palette
            int offset = 3 * int(random(0, (PALETTE.length - 1) / 3));
            
            return color(PALETTE[offset],  PALETTE[offset + 1], PALETTE[offset + 2], a);
        } else {
            return /** color **/ color(0, 0, 0, a) /** endcolor **/;
        }
    }
    
    PVector get_directional_vertex(PVector start, PVector end, float distance) {
        PVector offset = end;
        offset.sub(start);
        
        offset.normalize();
        offset.mult(distance);
        
        offset.add(start);
        return offset;
    }
    
    boolean update() {
        PVector rand = get_vertex();
        float min_dist = 999999;
        int min_i = -1;
        
        // find closest vertex to randomly chosen vertex
        for (int i = 0; i < _vertices.size(); i++) {
            PVector v = ((PVector) _vertices.get(i));
            
            if (v != null) {
                float cur_dist = rand.dist(v);
                
                if (cur_dist < min_dist) {
                    min_i = i;
                    min_dist = cur_dist;
                }
            }
        }
        
        if (min_i < 0) {
            return false;
        }
        
        PVector closest = ((PVector) _vertices.get(min_i));
        float distance  = random(_distance * /** float **/ 0.75 /** endfloat **/, 
                                 _distance * /** float **/ 1.25 /** endfloat **/);
        
        PVector newV    = get_directional_vertex(closest, rand, distance);
        int retry_max   = 6;
        int retries     = 0;
        
        while (retries++ < retry_max) {
            if (is_masked(int(newV.x), int(newV.y))) {
                break;
            }
            
            newV = get_directional_vertex(closest, rand, distance / retries);
        }
        
        if (retries > retry_max) {
            return true;
        }
        
        _vertices.add(newV);
        
        stroke(/** color **/ color(0, 0, 0, 120) /** endcolor **/);
        strokeWeight(/** float [ 0, 16 ] **/ 1.0 /** endfloat **/);
        
        if (CURVATURE <= 0) {
            line(closest.x, closest.y, newV.x, newV.y);
        } else {
            float curve_dist = distance * CURVATURE;
            
            PVector ctx0 = new PVector(closest.x + random(-curve_dist, curve_dist), 
                                       closest.y + random(-curve_dist, curve_dist));
            
            PVector ctx1 = new PVector(newV.x    + random(-curve_dist, curve_dist), 
                                       newV.y    + random(-curve_dist, curve_dist));
            
            /*
            PVector ctx1;
            retries = 0;
            
            while (retries++ < 6) {
                int ctx1_x = int(newV.x + random(-curve_dist, curve_dist)); 
                int ctx1_y = int(newV.y + random(-curve_dist, curve_dist));
                
                if (is_masked(ctx1_x, ctx1_y)) {
                    ctx1   = new PVector(ctx1_x, ctx1_y);
                    break;
                }
            }*/
            
            if (retries < 7) {
                bezier(closest.x, closest.y, 
                       ctx0.x, ctx0.y, 
                       ctx1.x, ctx1.y, 
                       newV.x, newV.y);
            }
        }
        
        stroke(/** color **/ color(255, 255, 255, 48) /** endcolor **/);
        
        int alpha0 = /** int [ 0, 255 ] **/ 10  /** endint **/;
        int alpha1 = /** int [ 0, 255 ] **/ 150 /** endint **/;
        
        if (alpha0 > alpha1) {
            int temp = alpha0;
            alpha0   = alpha1;
            alpha1   = temp;
        }
        
        fill(random_color(int(random(alpha0, alpha1))));
        ellipse(newV.x, newV.y, distance, distance);
        
        return true;
    }
}

// color palette extracted from a seed image
static int[] PALETTE = {
    71, 49, 19, 108, 63, 16, 99, 100, 68, 71, 125, 105, 82, 138, 113, 
    115, 148, 131, 108, 150, 148, 125, 148, 128, 174, 15, 68, 
    175, 77, 71, 195, 62, 69, 205, 91, 71, 176, 144, 94, 
    190, 170, 82, 204, 161, 75, 140, 157, 138, 157, 179, 154, 
    169, 182, 167, 188, 209, 195, 231, 193, 152, 20, 18, 34, 
    23, 88, 57, 66, 60, 46, 102, 70, 45, 96, 103, 89, 
    86, 124, 90, 102, 141, 72, 123, 152, 99, 118, 142, 138, 
    126, 150, 143, 171, 54, 71, 186, 71, 97, 217, 26, 74, 
    210, 78, 89, 185, 129, 91, 188, 143, 79, 181, 149, 100, 
    135, 156, 152, 141, 171, 167, 167, 184, 177, 206, 159, 141, 
    241, 194, 170, 16, 42, 20, 44, 68, 23, 97, 28, 17, 
    118, 75, 24, 115, 93, 55, 110, 110, 64, 113, 143, 82, 
    116, 154, 129, 117, 144, 152, 124, 152, 150, 145, 77, 14, 
    169, 115, 80, 218, 72, 69, 237, 74, 68, 202, 115, 90, 
    186, 144, 108, 185, 145, 116, 147, 147, 142, 143, 170, 175, 
    181, 171, 164, 214, 156, 161, 205, 208, 196, 19, 45, 39, 
    47, 72, 47, 99, 22, 41, 112, 74, 47, 109, 94, 78, 
    97, 109, 88, 85, 131, 100, 92, 138, 133, 121, 125, 117, 
    140, 39, 35, 141, 80, 44, 171, 120, 99, 200, 89, 42, 
    228, 97, 55, 208, 135, 82, 193, 160, 89, 187, 155, 108, 
    148, 149, 152, 145, 177, 167, 181, 182, 167, 210, 169, 144, 
    209, 217, 218, 39, 16, 24, 56, 90, 52, 101, 57, 21, 
    86, 77, 52, 96, 100, 75, 95, 119, 96, 79, 131, 127, 
    88, 135, 148, 121, 122, 129, 141, 14, 40, 148, 99, 24, 
    207, 25, 24, 206, 64, 40, 234, 105, 80, 211, 144, 108, 
    192, 165, 113, 189, 160, 119, 149, 157, 145, 147, 177, 177, 
    181, 188, 176, 201, 183, 165, 216, 223, 211, 43, 11, 37, 
    31, 80, 63, 94, 61, 49, 83, 79, 82, 94, 104, 99, 
    107, 124, 94, 98, 134, 107, 91, 135, 143, 110, 121, 131, 
    140, 51, 19, 144, 107, 44, 205, 9, 40, 205, 80, 28, 
    175, 116, 92, 163, 158, 124, 194, 171, 103, 202, 151, 104, 
    150, 158, 150, 150, 174, 171, 163, 190, 187, 223, 176, 149, 
    215, 223, 219, 43, 41, 26, 26, 95, 70, 64, 64, 71, 
    77, 89, 75, 70, 98, 107, 85, 113, 114, 98, 132, 120, 
    94, 134, 156, 114, 119, 150, 145, 57, 40, 168, 87, 18, 
    207, 42, 20, 207, 94, 37, 192, 119, 105, 192, 131, 82, 
    212, 145, 64, 197, 153, 122, 139, 159, 166, 152, 174, 178, 
    170, 188, 192, 234, 182, 165, 246, 207, 195, 44, 49, 40, 
    46, 81, 72, 96, 28, 69, 82, 77, 87, 63, 105, 119, 
    80, 120, 126, 97, 138, 124, 95, 144, 145, 118, 121, 137, 
    169, 27, 25, 174, 81, 42, 207, 50, 37, 228, 76, 25, 
    187, 113, 55, 183, 132, 57, 215, 147, 63, 199, 162, 107, 
    141, 164, 150, 150, 179, 170, 159, 191, 160, 241, 189, 187, 
    231, 222, 212, 28, 51, 67, 51, 80, 98, 104, 55, 73, 
    84, 86, 101, 66, 99, 124, 82, 122, 120, 97, 147, 126, 
    99, 144, 153, 126, 114, 140, 175, 15, 40, 175, 103, 23, 
    238, 21, 17, 241, 64, 35, 202, 111, 34, 200, 146, 29, 
    222, 164, 62, 196, 166, 121, 138, 168, 158, 152, 183, 178, 
    158, 192, 175, 203, 194, 160, 228, 231, 221, 26, 58, 90, 
    49, 95, 88, 77, 76, 46, 74, 100, 86, 73, 112, 125, 
    88, 130, 127, 97, 144, 133, 97, 136, 163, 125, 118, 145, 
    174, 46, 25, 175, 114, 39, 244, 14, 32, 242, 79, 27, 
    203, 120, 38, 200, 150, 45, 216, 176, 73, 189, 182, 122, 
    144, 171, 148, 164, 165, 147, 172, 195, 155, 204, 195, 156, 
    229, 231, 222, 43, 31, 70, 53, 104, 97, 70, 89, 58, 
    72, 109, 94, 83, 118, 141, 103, 126, 134, 108, 136, 121, 
    104, 141, 147, 127, 131, 141, 170, 56, 43, 147, 89, 65, 
    244, 42, 20, 239, 94, 35, 185, 126, 65, 202, 141, 49, 
    232, 168, 61, 197, 184, 118, 155, 166, 141, 170, 172, 149, 
    183, 196, 172, 220, 194, 133, 230, 231, 220, 44, 47, 69, 
    70, 44, 44, 74, 86, 36, 80, 105, 84, 93, 116, 130, 
    109, 127, 130, 112, 136, 127, 102, 144, 146, 116, 131, 128, 
    150, 30, 63, 144, 104, 77, 245, 48, 34, 220, 78, 57, 
    170, 120, 91, 198, 138, 68, 205, 146, 76, 156, 158, 132, 
    156, 167, 150, 167, 175, 162, 175, 196, 187, 213, 193, 147, 
    230, 231, 221, 21, 63, 36, 72, 15, 38, 76, 84, 46, 
    82, 105, 94, 71, 118, 105, 91, 135, 104, 113, 144, 120, 
    104, 149, 141, 114, 138, 129, 142, 53, 70, 141, 117, 98, 
    211, 26, 63, 203, 67, 86, 164, 135, 94, 200, 161, 57, 
    199, 150, 78, 143, 153, 141, 156, 176, 147, 167, 176, 179, 
    184, 200, 192, 199, 200, 179, 229, 232, 223, 
};

