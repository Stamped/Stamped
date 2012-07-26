//
//  STCalloutView.m
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import "STCalloutView.h"
#import "STConfiguration.h"

#define kCalloutHeight 54.0f
#define kMinWidth 120.0f

static NSString* const _fadeDurationKey = @"PopUp-ToolTip.fadeDuration";
static NSString* const _fadeDelayKey = @"PopUp-ToolTip.fadeDelay";

@implementation STCalloutView

- (void)commonInit {
    
    self.frame = CGRectMake(0.0f, 0.0f, kMinWidth, kCalloutHeight);
    
    UIImage *image = [UIImage imageNamed:@"st_callout_left.png"];
    UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:image.size.width-1 topCapHeight:0]];
    [self addSubview:imageView];
    [imageView release];
    _left = imageView;
    
    image = [UIImage imageNamed:@"st_callout_right.png"];
    imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:1.0f topCapHeight:0]];
    [self addSubview:imageView];
    [imageView release];
    _right = imageView;
    
    imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"st_callout_mid.png"]];
    [self addSubview:imageView];
    [imageView release];
    _mid = imageView;
    
}

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:CGRectZero])) {
        [self commonInit];
    }
    return self;
}

- (id)init {
    if ((self = [super initWithFrame:CGRectZero])) {
        [self commonInit];
    }
    return self;
}

- (void)showFromPosition:(CGPoint)position animated:(BOOL)animated {
    
    UIView *view = self.superview;
    CGRect frame = self.frame;
    CGFloat arrowLocation = (frame.size.width/2);
    CGFloat diff = 0.0f;
    
    frame.origin.x = position.x - (frame.size.width/2);
    
    if (frame.origin.x < (view.frame.origin.x+14)) {
        
        diff = ((view.frame.origin.x+14) - frame.origin.x);
        arrowLocation = (frame.size.width/2) - diff;
        frame.origin.x = (view.frame.origin.x+14);
        
    } else if (CGRectGetMaxX(frame) > (view.frame.size.width-14)) {
        
        diff = ((view.frame.size.width-14) - CGRectGetMaxX(frame));
        arrowLocation = (frame.size.width/2) - diff;
        frame.origin.x = (view.frame.size.width-14) - frame.size.width;
        
    } 
    
    arrowLocation = MIN(arrowLocation, frame.size.width - 20);
    arrowLocation = MAX(20, arrowLocation);
    
    frame.origin.y = position.y - self.bounds.size.height;
    self.frame = frame;
    
    frame = _mid.frame;
    frame.origin.x = arrowLocation - (_mid.bounds.size.width/2);
    _mid.frame = frame;
    
    frame = _left.frame;
    frame.size.width = CGRectGetMinX(_mid.frame);
    _left.frame = frame;
    
    frame = _right.frame;
    frame.origin.x = CGRectGetMaxX(_mid.frame);
    frame.size.width = self.bounds.size.width - CGRectGetMaxX(_mid.frame);
    _right.frame = frame;
    
    if (animated) {
        
        CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
        scale.duration = 0.45f;
        scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:.5f], [NSNumber numberWithFloat:1.2f], [NSNumber numberWithFloat:.85f], [NSNumber numberWithFloat:1.f], nil];
        
        CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
        opacity.duration = 0.45f * .4f;
        opacity.fromValue = [NSNumber numberWithFloat:0.f];
        opacity.toValue = [NSNumber numberWithFloat:1.f];
        opacity.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut];
        opacity.fillMode = kCAFillModeForwards;
        
        CAAnimationGroup *animation = [CAAnimationGroup animation];
        [animation setAnimations:[NSArray arrayWithObjects:scale, opacity, nil]];
        animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
        [self.layer addAnimation:animation forKey:nil];
        
    }
    
}

- (void)hide:(BOOL)animated {
    [UIView animateWithDuration:[[STConfiguration value:_fadeDurationKey] floatValue]
                          delay:[[STConfiguration value:_fadeDelayKey] floatValue] 
                        options:UIViewAnimationOptionCurveEaseOut 
                     animations:^{
                         self.alpha = 0; 
                     } completion:^(BOOL finished) {
                         self.alpha = 1;
                         self.hidden = YES;
                     }];
}

+ (void)setupConfigurations {
    [STConfiguration addNumber:[NSNumber numberWithFloat:.4] forKey:_fadeDurationKey];
    [STConfiguration addNumber:[NSNumber numberWithFloat:.9] forKey:_fadeDelayKey];
}

@end
