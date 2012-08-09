/*! displaced.pde
 * 
 * @author: Travis Fischer
 * @date:   December 2008 (Java)
 * @port:   August 2012 to processing.js
 */

/* @pjs preload="displaced1.jpeg"; */

static int SIMULATION_WIDTH  = 640;
static int SIMULATION_HEIGHT = 480;

boolean _automaticWaves;

int _rippleRadius;
int _strength;

int[] _map0;
int[] _map1;

PImage  _offscreen;
color[] _back;

void setup() {
    size(SIMULATION_WIDTH, SIMULATION_HEIGHT);
    frameRate(32);
    loop();
    
    _rippleRadius   = 3; // 2 to 3 works well
    _strength       = 4; // 3 to 9 works well
    _automaticWaves = true;
    _offscreen      = createImage(width, height, RGB);
    
    reset();
}

void reset() {
    background(#FFFFFF);
    
    _map0 = new int[width * height];
    _map1 = new int[width * height];
    
    loadBackground(loadImage("displaced1.jpeg"));
}

void draw() {
    update();
    
    image(_offscreen, 0, 0);
}

void update() {
    int[] temp = _map0;
    
    _map0 = _map1;
    _map1 = temp;
    
    if (_automaticWaves) {
        this.disturb(int(random(1, width - 2)), int(random(1, height - 2)));
    }
    
    for(int index = 0, int j = 0; j < height; j++) {
        int a = (j <= 0 ? 0 : width);
        int b = (j >= height - 1 ? 0 : width);
        
        for(int i = 0; i < width; i++, index++) {
            int old = _map0[index];
            int avg = (int)(((_map1[index - a] + _map1[index + b] + 
                              _map1[index - (i <= 0 ? 0 : 1)] + 
                              _map1[index + (i >= width - 1 ? 0 : 1)]) >> 1) - old);
            
            // dampen the strength of the wave over time
            avg -= (avg >> _strength);
            
            if (old != avg) {
                _map0[index] = avg;
                
                int x = i, y = j;
                
                if (avg > 0 && avg < 1024) {
                    avg = (int)(1024 - avg);
                    
                    // reflect (i, j) incides based on current magnitude of wave
                    x = (i * avg) >> 10;
                    y = (j * avg) >> 10;
                    
                    // Boundary checks
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
    
    for(int a = 0, j = 0; j < image.height; j++) {
        for(int i = 0; i < image.width; i++) {
            color temp = image.get(i, j);
            _back[a++] = temp;
            
            _offscreen.set(i, j, temp);
        }
    }
}

void disturb(int x, int y) {
    _rippleRadius = int(random(1, 3));
    
    for(int j = -_rippleRadius; j <= _rippleRadius; j++) {
        int val = (int)(8 - _rippleRadius - abs(j));
        
        int yOff = y + j;
        if (yOff >= 0 && yOff < height) {
            yOff *= width;
            
            for(int i = -_rippleRadius; i <= _rippleRadius; i++) {
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
    this.disturb(mouseX, mouseY);
}

void mouseDragged() {
    this.disturb(mouseX, mouseY);
}

