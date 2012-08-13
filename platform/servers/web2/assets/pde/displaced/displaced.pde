/*! displaced.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing
 * 
 * Old-school wave simulation.
 */

/* @pjs preload="/assets/pde/displaced/displaced0.jpeg"; */
/* @pjs preload="/assets/pde/displaced/displaced1.jpeg"; */

static boolean AUTOMATIC_WAVES      = /** boolean      **/ true /** endboolean **/;
static int     RIPPLE_RADIUS        = /** int [ 2, 4 ] **/ 3    /** endint     **/;
static int     RIPPLE_STRENGTH      = /** int [ 3, 9 ] **/ 4    /** endint     **/;
static int BACKGROUND_IMAGE_INDEX   = /** int [ 0, 1 ] **/ 1    /** endint     **/;

static String[] BACKGROUND_IMAGES;

int[] _map0;
int[] _map1;

PImage  _offscreen;
color[] _back;

void setup() {
    size(/** int ( 0, 1024 ] **/ 640 /** endint **/, /** int ( 0, 1024 ] **/ 480 /** endint **/);
    frameRate(/** int [ 1, 60 ] **/ 12 /** endint **/);
    loop();
    
    BACKGROUND_IMAGES = new String[2];
    BACKGROUND_IMAGES[0] = "/assets/pde/displaced/displaced0.jpeg";
    BACKGROUND_IMAGES[1] = "/assets/pde/displaced/displaced1.jpeg";
    
    reset();
}

void reset() {
    background(/** color **/ #FFFFFF /** endcolor **/);
    
    _offscreen = createImage(width, height, RGB);
    
    _map0 = new int[width * height];
    _map1 = new int[width * height];
    
    loadBackground(loadImage(BACKGROUND_IMAGES[BACKGROUND_IMAGE_INDEX]));
}

void draw() {
    update();
    
    image(_offscreen, 0, 0);
}

void update() {
    int[] temp = _map0;
    int index  = 0;
    
    _map0 = _map1;
    _map1 = temp;
    
    if (AUTOMATIC_WAVES) {
        disturb(int(random(1, width - 2)), int(random(1, height - 2)));
    }
    
    for(int j = 0; j < height; j++) {
        int a = (j <= 0 ? 0 : width);
        int b = (j >= height - 1 ? 0 : width);
        
        for(int i = 0; i < width; i++, index++) {
            int old = _map0[index];
            int avg = (int)(((_map1[index - a] + _map1[index + b] + 
                              _map1[index - (i <= 0 ? 0 : 1)] + 
                              _map1[index + (i >= width - 1 ? 0 : 1)]) >> 1) - old);
            
            // dampen the strength of the wave over time
            avg -= (avg >> RIPPLE_STRENGTH);
            
            if (old != avg) {
                _map0[index] = avg;
                
                int x = i, y = j;
                
                if (avg > 0 && avg < 1024) {
                    avg = (int)(1024 - avg);
                    
                    // reflect (i, j) incides based on current magnitude of wave
                    x = (i * avg) >> 10;
                    y = (j * avg) >> 10;
                    
                    // boundary checks
                    x = (x <= 0 ? 0 : (x >= width  ? width  - 1 : x));
                    y = (y <= 0 ? 0 : (y >= height ? height - 1 : y));
                }
                
                _offscreen.set(i, j, _back[y * width + x]);
            }
        }
    }
}

void loadBackground(PImage image) {
    if (image.width != width || image.height != height) {
        image.resize(width, height);
    }
    
    _back = new color[image.width * image.height];
    
    int index = 0;
    
    for(int j = 0; j < image.height; j++) {
        for(int i = 0; i < image.width; i++) {
            color temp     = image.get(i, j);
            _back[index++] = temp;
            
            _offscreen.set(i, j, temp);
        }
    }
}

void disturb(int x, int y) {
    int radius = RIPPLE_RADIUS;
    
    if (AUTOMATIC_WAVES) {
        radius = int(random(1, 3));
    }
    
    // apply a weighted filter to the height-field centered around the disturbance point
    for(int j = -radius; j <= radius; j++) {
        int val = (int)(8 - radius - abs(j));
        
        int yOff = y + j;
        if (yOff >= 0 && yOff < height) {
            yOff *= width;
            
            for(int i = -radius; i <= radius; i++) {
                val += (i <= 0 ? 1 : -1);
                
                int xOff = x + i;
                if (xOff >= 0 && xOff < width) {
                    _map1[yOff + xOff] = (int)(1 << val);
                }
            }
        }
    }
}

void mousePressed() {
    disturb(mouseX, mouseY);
}

void mouseDragged() {
    disturb(mouseX, mouseY);
}

