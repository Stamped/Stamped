//
//  CreateComposeView.m
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import "STStampContainerView.h"

@implementation STStampContainerView

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        UIImage *image = [UIImage imageNamed:@"create_wave_pttrn.png"];

        STBlockUIView *container = [[STBlockUIView alloc] initWithFrame:CGRectInset(self.bounds, 5, 5)];
        container.backgroundColor = [UIColor whiteColor];
        container.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:container];
        container.layer.shadowOffset = CGSizeMake(0.0f, 4.0f);
        container.layer.shadowRadius = 7.5f;
        container.layer.shadowColor = [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.2f].CGColor;
        container.layer.shadowOpacity = 1.0f;
        container.layer.shadowPath = [UIBezierPath bezierPathWithRect:container.bounds].CGPath;
        [container setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            
            rect = CGRectInset(rect, 0, 1);
            CGContextClipToRect(ctx, rect);
           
            id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
            
            CGFloat r,b,g,r1,b1,g1;
            [Util splitHexString:user.primaryColor toRed:&r green:&g blue:&b];
            [Util splitHexString:user.secondaryColor toRed:&r1 green:&g1 blue:&b1];
            
            CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
            size_t _numLocations = 2;
            CGFloat _locations[2] = { 0.0, 1.0 };
            CGFloat _colors[8] = { r, g, b, 1.0f, r1, g1, b1, 1.0f };
            CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
            CGColorSpaceRelease(_rgb);
            CGPoint start = CGPointMake(rect.origin.x, rect.origin.y + rect.size.height);
            CGPoint end = CGPointMake(rect.origin.x + rect.size.width, rect.origin.y);
            CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsAfterEndLocation);
            CGGradientRelease(gradient);
            
        }];
        _containerView = container;
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectInset(container.bounds, 0, 1)];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleHeight;
        imageView.image = [image stretchableImageWithLeftCapWidth:0.0f topCapHeight:(image.size.height/2)];
        [container addSubview:imageView];
        [imageView release];
        [container release];

    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    _containerView.layer.shadowPath = [UIBezierPath bezierPathWithRect:_containerView.bounds].CGPath;
    
}



@end


