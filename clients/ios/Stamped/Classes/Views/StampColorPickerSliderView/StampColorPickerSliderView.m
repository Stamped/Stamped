//
//  StampColorPickerSliderView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "StampColorPickerSliderView.h"

@interface StampColorPickerSliderView ()
- (void)resetBrightnessSlider;
@end

@implementation StampColorPickerSliderView
@synthesize delegate;
@synthesize color1;
@synthesize color2;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

        UIImage *track = [UIImage imageNamed:@"stamp_color_slider_hue_track.png"];
        UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake((self.bounds.size.width-track.size.width)/2, 10.0f, track.size.width, 40.0f)];
        [slider setMinimumTrackImage:track forState:UIControlStateNormal];
        [slider setMaximumTrackImage:track forState:UIControlStateNormal];
        [slider setThumbImage:[UIImage imageNamed:@"stamp_color_slider_thumb.png"] forState:UIControlStateNormal];
        [slider addTarget:self action:@selector(hueChanged:) forControlEvents:UIControlEventValueChanged];
        [self addSubview:slider];
        [slider release];
        _hueSlider = slider;
        
        slider = [[UISlider alloc] initWithFrame:CGRectMake((self.bounds.size.width-track.size.width)/2, 50.0f, track.size.width, 40.0f)];
        [slider setThumbImage:[UIImage imageNamed:@"stamp_color_slider_thumb.png"] forState:UIControlStateNormal];
        [slider addTarget:self action:@selector(brightnessChanged:) forControlEvents:UIControlEventValueChanged];
        [self addSubview:slider];
        [slider release];
        _brightnessSlider = slider;
        
    }
    return self;
}

- (void)colorChanged {
    
    if ([(id)delegate respondsToSelector:@selector(stampColorPickerSliderView:pickedColors:)]) {
        [self.delegate stampColorPickerSliderView:self pickedColors:[NSArray arrayWithObjects:self.color1, self.color2, nil]];
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

- (void)hueChanged:(UISlider*)slider {
    
    [self resetBrightnessSlider];
    
}

- (void)brightnessChanged:(UISlider*)slider {
    
    
}


#pragma mark - Getters

- (NSArray*)colors {
    
    return [NSArray arrayWithObjects:self.color1, self.color2, nil];
    
}


@end
