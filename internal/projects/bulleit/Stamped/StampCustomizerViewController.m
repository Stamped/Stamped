//
//  StampCustomizerViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampCustomizerViewController.h"

#import "Util.h"

@interface StampCustomizerViewController ()
- (void)hueChanged:(id)sender;
- (void)brightnessChanged:(id)sender;
- (void)setColor:(UIColor*)color forButton:(UIButton*)button;
@end

@implementation StampCustomizerViewController

@synthesize brightnessSlider = brightnessSlider_;
@synthesize hueSlider = hueSlider_;
@synthesize stampImageView = stampImageView_;
@synthesize primaryColorButton = primaryColorButton_;
@synthesize secondaryColorButton = secondaryColorButton_;
@synthesize delegate = delegate_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

- (void)dealloc {
  self.brightnessSlider = nil;
  self.hueSlider = nil;
  self.stampImageView = nil;
  self.primaryColorButton = nil;
  self.secondaryColorButton = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  primaryHue_ = 0.75;
  primaryBrightness_ = 0.25;
  secondaryHue_ = 0.75;
  secondaryBrightness_ = 0.25;
  primaryColorButton_.selected = YES;
  [hueSlider_ setMinimumTrackImage:[UIImage imageNamed:@"hue_background"] forState:UIControlStateNormal];
  [hueSlider_ setMaximumTrackImage:[UIImage imageNamed:@"hue_background"] forState:UIControlStateNormal];
  [hueSlider_ addTarget:self
                 action:@selector(hueChanged:)
       forControlEvents:UIControlEventValueChanged];
  [self hueChanged:hueSlider_];
  [brightnessSlider_ addTarget:self
                        action:@selector(brightnessChanged:)
              forControlEvents:UIControlEventValueChanged];
  [self brightnessChanged:brightnessSlider_];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.brightnessSlider = nil;
  self.hueSlider = nil;
  self.stampImageView = nil;
  self.primaryColorButton = nil;
  self.secondaryColorButton = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Private methods.

- (void)primaryColorButtonPressed:(id)sender {
  primaryColorButton_.selected = YES;
  secondaryColorButton_.selected = NO;
  [hueSlider_ setValue:primaryHue_ animated:YES];
  [brightnessSlider_ setValue:primaryBrightness_ animated:YES];
}

- (void)secondaryColorButtonPressed:(id)sender {
  secondaryColorButton_.selected = YES;
  primaryColorButton_.selected = NO;
  [hueSlider_ setValue:secondaryHue_ animated:YES];
  [brightnessSlider_ setValue:secondaryBrightness_ animated:YES];
}

- (void)setColor:(UIColor*)color forButton:(UIButton*)button {
  CGFloat width = 25;
  CGFloat height = 25;
  UIGraphicsBeginImageContextWithOptions(CGSizeMake(width, height), NO, 0.0);
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, color.CGColor);
  CGContextFillEllipseInRect(ctx, CGRectMake(0, 0, width, height));
  [[UIImage imageNamed:@"color_dropshadow"] drawInRect:CGRectMake(0, 0, width, height)];
  [button setImage:UIGraphicsGetImageFromCurrentImageContext() forState:UIControlStateNormal];
  UIGraphicsEndImageContext();
}

- (void)hueChanged:(id)sender {
  if (primaryColorButton_.selected) {
    primaryHue_ = hueSlider_.value;
  } else if (secondaryColorButton_.selected) {
    secondaryHue_ = hueSlider_.value;
  }

  UIImage* brightnessBorder = [UIImage imageNamed:@"brightness_border"];
  
  CGFloat width = brightnessBorder.size.width;
  CGFloat height = brightnessBorder.size.height;
  CGRect rect = CGRectMake(0, 0, width, height);
  
  UIColor* darkHueColor = [UIColor colorWithHue:hueSlider_.value
                                     saturation:1.0
                                     brightness:0.1
                                          alpha:1.0];
  UIColor* lightHueColor = [UIColor colorWithHue:hueSlider_.value
                                      saturation:1.0
                                      brightness:1.0
                                           alpha:1.0];
  UIColor* clearHueColor = [UIColor colorWithHue:hueSlider_.value
                                      saturation:1.0
                                      brightness:1.0
                                           alpha:0.2];
  NSArray* colorsArray = [NSArray arrayWithObjects:(id)darkHueColor.CGColor,
                                                   (id)lightHueColor.CGColor,
                                                   (id)clearHueColor.CGColor, nil];

  UIGraphicsBeginImageContextWithOptions(brightnessBorder.size, NO, 0.0);
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  
  UIBezierPath* path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, 0.5, 1)
                                                  cornerRadius:5];
  CGContextSaveGState(ctx);
  CGContextAddPath(ctx, path.CGPath);
  CGContextSetFillColorWithColor(ctx, [UIColor whiteColor].CGColor);
  CGContextFillPath(ctx);
  CGContextRestoreGState(ctx);
  CGContextSaveGState(ctx);
  CGContextAddPath(ctx, path.CGPath);
  CGContextClip(ctx);
  CGGradientRef gradient = CGGradientCreateWithColors(NULL, (CFArrayRef)colorsArray, NULL);
  CGContextDrawLinearGradient(ctx, gradient, CGPointMake(0, 0), CGPointMake(CGRectGetWidth(rect), 0), 0);
  CGGradientRelease(gradient);
  CGContextRestoreGState(ctx);
  [brightnessBorder drawInRect:CGRectMake(0, 0, width, height)];
  UIImage* brightnessImage = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  [brightnessSlider_ setMinimumTrackImage:brightnessImage forState:UIControlStateNormal];
  [brightnessSlider_ setMaximumTrackImage:brightnessImage forState:UIControlStateNormal];
  [self brightnessChanged:brightnessSlider_];
}

- (void)brightnessChanged:(id)sender {
  CGFloat value = brightnessSlider_.value;
  if (primaryColorButton_.selected) {
    primaryBrightness_ = value;
  } else if (secondaryColorButton_.selected) {
    secondaryBrightness_ = value;
  }
  CGFloat brightness = 1.0;
  CGFloat alpha = 1.0;
  if (value <= 0.5) {
    brightness = ((1.0 - 0.1) * (value / 0.5)) + 0.1;
  } else {
    alpha = ((1.0 - 0.2) * ((1 - value) / 0.5)) + 0.2;
  }
  UIColor* result = [UIColor colorWithHue:hueSlider_.value
                               saturation:1.0
                               brightness:brightness
                                    alpha:alpha];
  if (CGColorGetNumberOfComponents(result.CGColor) == 4) {
    const CGFloat* components = CGColorGetComponents(result.CGColor);
    CGFloat a = components[3];  // Alpha channel.
    CGFloat r = a * components[0] + (1 - a);
    CGFloat g = a * components[1] + (1 - a);
    CGFloat b = a * components[2] + (1 - a);
    if (primaryColorButton_.selected) {
      primaryRed_ = r;
      primaryGreen_ = g;
      primaryBlue_ = b;
      [self setColor:[UIColor colorWithRed:r green:g blue:b alpha:1.0] forButton:primaryColorButton_];

      if (!secondaryRed_ && !secondaryBlue_ && !secondaryGreen_) {
        secondaryRed_ = r;
        secondaryGreen_ = g;
        secondaryBlue_ = b;
        [self setColor:[UIColor colorWithRed:r green:g blue:b alpha:1.0] forButton:secondaryColorButton_];
      }
    } else if (secondaryColorButton_.selected) {
      secondaryRed_ = r;
      secondaryGreen_ = g;
      secondaryBlue_ = b;
      [self setColor:[UIColor colorWithRed:r green:g blue:b alpha:1.0] forButton:secondaryColorButton_];
    }
    UIImage* stampImage = [Util gradientImage:[UIImage imageNamed:@"stamp_270pt_texture"]
                               withPrimaryRed:primaryRed_
                                 primaryGreen:primaryGreen_
                                  primaryBlue:primaryBlue_
                                 secondaryRed:secondaryRed_
                               secondaryGreen:secondaryGreen_
                                secondaryBlue:secondaryBlue_];
    stampImageView_.image = stampImage;
  } else {
    NSLog(@"The color didn't have 4 components... hmmmm");
  }
}

#pragma mark - Actions

- (IBAction)cancelButtonPressed:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

- (IBAction)doneButtonPressed:(id)sender {
  NSInteger redIntValue = primaryRed_ * 255.99999f;
  NSInteger greenIntValue = primaryGreen_ * 255.99999f;
  NSInteger blueIntValue = primaryBlue_ * 255.99999f;

  NSString* redHexValue = [NSString stringWithFormat:@"%02x", redIntValue]; 
  NSString* greenHexValue = [NSString stringWithFormat:@"%02x", greenIntValue];
  NSString* blueHexValue = [NSString stringWithFormat:@"%02x", blueIntValue];

  NSString* primaryColor = [NSString stringWithFormat:@"%@%@%@", redHexValue, greenHexValue, blueHexValue];
  
  redIntValue = secondaryRed_ * 255.99999f;
  greenIntValue = secondaryGreen_ * 255.99999f;
  blueIntValue = secondaryBlue_ * 255.99999f;
  
  redHexValue = [NSString stringWithFormat:@"%02x", redIntValue]; 
  greenHexValue = [NSString stringWithFormat:@"%02x", greenIntValue];
  blueHexValue = [NSString stringWithFormat:@"%02x", blueIntValue];
  
  NSString* secondaryColor = [NSString stringWithFormat:@"%@%@%@", redHexValue, greenHexValue, blueHexValue];
  
  [delegate_ stampCustomizer:self chosePrimaryColor:primaryColor secondaryColor:secondaryColor];
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

@end
