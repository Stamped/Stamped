//
//  StampColorPickerSliderView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "StampColorPickerSliderView.h"

@interface StampColorPickerColorView : UIControl {
    UIView *_colorView;
    UIView *_backgroundView;
}
@property(nonatomic,assign) CGFloat brightness;
@property(nonatomic,assign) CGFloat hue;
@property(nonatomic,retain) UIColor *color;
@end

@interface StampColorPickerSliderView ()
- (void)resetBrightnessSlider;
@end

@implementation StampColorPickerSliderView
@synthesize delegate;
@synthesize colors=_colors;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        
        StampColorPickerColorView *view = [[StampColorPickerColorView alloc] initWithFrame:CGRectMake(80.0f, 14.0f, 38.0f, 38.0f)];
        [view addTarget:self action:@selector(colorViewSelected:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:view];
        [view release];
        _firstColorView = view;
        _firstColorView.selected = YES;
        
        view = [[StampColorPickerColorView alloc] initWithFrame:CGRectMake(self.bounds.size.width - 118.0f, 14.0f, 38.0f, 38.0f)];
        [view addTarget:self action:@selector(colorViewSelected:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:view];
        [view release];
        _secondColorView = view;
        
        UIView *container = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 50.0f, self.bounds.size.width, self.bounds.size.height - 50.0f)];
        [self addSubview:container];
        
        UIImage *image = [UIImage imageNamed:@"stamp_color_slider_hud_bg.png"];
        UIImageView *hud = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        [container addSubview:hud];
        [hud release];
    
        CGRect frame = hud.frame;
        frame.origin.y = container.bounds.size.height - (image.size.height+6.0f);
        frame.origin.x = 10.0f;
        frame.size.width = self.bounds.size.width - 20.0f;
        hud.frame = frame;
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_color_slider_arrow.png"]];
        [container addSubview:imageView];
        [imageView release];
        _arrowView = imageView;
        
        frame = imageView.frame;
        frame.origin.y = hud.frame.origin.y - (frame.size.height-4.0f);
        frame.origin.x = CGRectGetMidX(_firstColorView.frame) - (frame.size.width/2);
        imageView.frame = frame;

        UIImage *track = [UIImage imageNamed:@"stamp_color_slider_hue_track.png"];
        UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake((self.bounds.size.width-track.size.width)/2, 18.0f, track.size.width, 40.0f)];
        [slider setMinimumTrackImage:track forState:UIControlStateNormal];
        [slider setMaximumTrackImage:track forState:UIControlStateNormal];
        [slider setThumbImage:[UIImage imageNamed:@"stamp_color_slider_thumb.png"] forState:UIControlStateNormal];
        [slider addTarget:self action:@selector(hueChanged:) forControlEvents:UIControlEventValueChanged];
        [container addSubview:slider];
        [slider release];
        _hueSlider = slider;
        
        slider = [[UISlider alloc] initWithFrame:CGRectMake((self.bounds.size.width-track.size.width)/2, 56.0f, track.size.width, 40.0f)];
        [slider setThumbImage:[UIImage imageNamed:@"stamp_color_slider_thumb.png"] forState:UIControlStateNormal];
        [slider addTarget:self action:@selector(brightnessChanged:) forControlEvents:UIControlEventValueChanged];
        [container addSubview:slider];
        [slider release];
        _brightnessSlider = slider;
        
        [container release];
        
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)colorChanged {
    
    if ([(id)delegate respondsToSelector:@selector(stampColorPickerSliderView:pickedColors:)]) {
        [self.delegate stampColorPickerSliderView:self pickedColors:[self colors]];
    }
    
}

- (void)resetBrightnessSlider {
    
    UIImage *image = [UIImage imageNamed:@"stamp_color_slider_brighness_track.png"];
    
    UIColor *dark = [UIColor colorWithHue:_hueSlider.value saturation:1.0 brightness:0.1 alpha:1.0];
    UIColor *light = [UIColor colorWithHue:_hueSlider.value saturation:1.0 brightness:1.0 alpha:1.0];
    UIColor *clear = [UIColor colorWithHue:_hueSlider.value saturation:1.0  brightness:1.0 alpha:0.2];
    NSArray *colorsArray = [NSArray arrayWithObjects:(id)dark.CGColor, (id)light.CGColor, (id)clear.CGColor, nil];
    
    UIGraphicsBeginImageContextWithOptions(image.size, NO, 0.0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    
    UIBezierPath *path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, 0.5, 1) cornerRadius:5];
    
    CGContextAddPath(ctx, path.CGPath);
    CGContextSetFillColorWithColor(ctx, [UIColor whiteColor].CGColor);
    CGContextFillPath(ctx);
    
    CGContextSaveGState(ctx);
    CGContextAddPath(ctx, path.CGPath);
    CGContextClip(ctx);
    CGGradientRef gradient = CGGradientCreateWithColors(NULL, (CFArrayRef)colorsArray, NULL);
    CGContextDrawLinearGradient(ctx, gradient, CGPointMake(0, 0), CGPointMake(CGRectGetWidth(rect), 0), 0);
    CGGradientRelease(gradient);
    CGContextRestoreGState(ctx);
    
    [image drawInRect:rect];
    
    UIImage *brightnessImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    [_brightnessSlider setMinimumTrackImage:brightnessImage forState:UIControlStateNormal];
    [_brightnessSlider setMaximumTrackImage:brightnessImage forState:UIControlStateNormal];

}


#pragma mark - Actions

- (void)colorViewSelected:(StampColorPickerColorView*)sender {
    
    _firstColorView.selected = NO;
    _secondColorView.selected = NO;
    [_hueSlider setValue:sender.hue animated:YES];
    [_brightnessSlider setValue:sender.brightness animated:YES];
    [self resetBrightnessSlider];
    sender.selected = YES;
    
    [UIView animateWithDuration:0.2f animations:^{
        CGRect frame = _arrowView.frame;
        frame.origin.x = CGRectGetMidX(sender.frame) - (frame.size.width/2);
        _arrowView.frame = frame;
    }];
    
}

- (void)hueChanged:(UISlider*)slider {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(resetBrightnessSlider) object:nil];
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(colorChanged) object:nil];

    if (_firstColorView.selected) {
        _firstColorView.hue = slider.value;
    } else if (_secondColorView.selected) {
        _secondColorView.hue = slider.value;
    }
    
    CGFloat alpha = 1.0;
    if (_brightnessSlider.value > 0.5) {
        alpha = ((1.0 - 0.2) * ((1 - _brightnessSlider.value) / 0.5)) + 0.2;
    }
    StampColorPickerColorView *selectedView = _firstColorView.selected ? _firstColorView : _secondColorView;
    UIColor *result = [UIColor colorWithHue:slider.value saturation:1.0 brightness:selectedView.brightness alpha:alpha];
    selectedView.color = result;
        
    [self performSelector:@selector(resetBrightnessSlider) withObject:nil afterDelay:0.05f];
    [self performSelector:@selector(colorChanged) withObject:nil afterDelay:0.05f];
    
}

- (void)brightnessChanged:(UISlider*)slider {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(colorChanged) object:nil];

    CGFloat value = slider.value;
    CGFloat brightness = 1.0;
    CGFloat alpha = 1.0;
    if (value <= 0.5) {
        brightness = ((1.0 - 0.1) * (value / 0.5)) + 0.1;
    } else {
        alpha = ((1.0 - 0.2) * ((1 - value) / 0.5)) + 0.2;
    }
    
    UIColor *result = [UIColor colorWithHue:_hueSlider.value saturation:1.0 brightness:brightness alpha:alpha];

    if (_firstColorView.selected) {
        _firstColorView.brightness = value;
        _firstColorView.color = result;
    } else if (_secondColorView.selected) {
        _secondColorView.brightness = value;
        _secondColorView.color = result;
    }
    
    [self performSelector:@selector(colorChanged) withObject:nil afterDelay:0.05f];
    
}


#pragma mark - Getters

- (NSArray*)colors {
    
    return [NSArray arrayWithObjects:_firstColorView.color, _secondColorView.color, nil];
    
}


#pragma mark - Setters

- (void)setColors:(NSArray *)colors {
    if (!colors || [colors count] < 2) return;
    
    _firstColorView.color = [colors objectAtIndex:0];
    _secondColorView.color = [colors objectAtIndex:1];

    CGFloat saturation, hue, brightness;
    [self getHue:&hue saturation:&saturation brightness:&brightness alpha:NULL fromColor:_firstColorView.color];
    if (saturation < 1.0) {
         brightness = ((-0.5 * (saturation - 1)) / 0.8) + 0.5;
    } else {
         brightness *= 0.5;
    }
    _firstColorView.hue = hue;
    _firstColorView.brightness = brightness;
    
    [self getHue:&hue saturation:&saturation brightness:&brightness alpha:NULL fromColor:_secondColorView.color];
    if (saturation < 1.0) {
        brightness = ((-0.5 * (saturation - 1)) / 0.8) + 0.5;
    } else {
        brightness *= 0.5;
    }
    _secondColorView.hue = hue;
    _secondColorView.brightness = brightness;
    
    StampColorPickerColorView *selectedView = _firstColorView.selected ? _firstColorView : _secondColorView;
    _brightnessSlider.value = selectedView.brightness;
    _hueSlider.value = selectedView.hue;
    
    [self resetBrightnessSlider];

}


#pragma mark - Color Helper 

- (void)getHue:(CGFloat*)hue saturation:(CGFloat*)saturation brightness:(CGFloat*)brightness alpha:(CGFloat*)alpha fromColor:(UIColor*)color {
    if ([color respondsToSelector:@selector(getHue:saturation:brightness:alpha:)]) {
        [color getHue:hue saturation:saturation brightness:brightness alpha:alpha];
        return;
    }
    CGColorRef colorRef = color.CGColor;
    size_t numComponents = CGColorGetNumberOfComponents(colorRef);
    if (numComponents < 4)
        return;
    
    const CGFloat* components = CGColorGetComponents(colorRef);
    CGFloat r = components[0];
    CGFloat g = components[1];
    CGFloat b = components[2];
    
    CGFloat min, max, delta;
    min = MIN(MIN(r, g), b);
    max = MAX(MAX(r, g), b);
    *brightness = max;
    delta = max - min;
    if (max != 0)
        *saturation = delta / max;
    else {
        // r = g = b = 0
        // s = 0, brightness is undefined
        *saturation = 0;
        *hue = -1;
        return;
    }
    if (r == max)
        *hue = (g - b) / delta;
    else if(g == max)
        *hue = 2 + (b - r) / delta;
    else
        *hue = 4 + (r - g) / delta;
    *hue *= 60;
    if (*hue < 0)
        *hue += 360;
    
    *hue = (*hue / 360);
}



@end


#pragma mark - StampColorPickerColorView

@implementation StampColorPickerColorView
@synthesize brightness;
@synthesize hue;
@synthesize color=_color;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectInset(self.bounds, 2.0f, 2.0f)];
        background.userInteractionEnabled = NO;
        background.backgroundColor = [UIColor whiteColor];
        background.layer.shadowPath = [UIBezierPath bezierPathWithRect:background.bounds].CGPath;
        background.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        background.layer.shadowRadius = 1.0f;
        background.layer.shadowOpacity = 0.2f;
        background.layer.rasterizationScale = [[UIScreen mainScreen] scale];
        background.layer.shouldRasterize = YES;
        [self addSubview:background];
        [background release];
        _backgroundView = background;
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectInset(self.bounds, 4.0f, 4.0f)];
        view.userInteractionEnabled = NO;
        view.backgroundColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:view];
        _colorView = view;
        [view release];
        
    }
    return self;
    
}

- (void)dealloc {
    [_color release], _color=nil;
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    if (!self.selected) return;
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextSetAlpha(ctx, 0.4f);
    CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:2.0f].CGPath);
    CGContextClip(ctx);
    drawGradient([UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f].CGColor, [UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f].CGColor, ctx);
    
    
}

- (void)setColor:(UIColor *)color {
    [_color release], _color=nil;
    _color = [color retain];
    _colorView.backgroundColor = _color;
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    
    _backgroundView.layer.shadowOpacity = selected ? 0.0f : 0.2f;
    [self setNeedsDisplay];

}

@end

