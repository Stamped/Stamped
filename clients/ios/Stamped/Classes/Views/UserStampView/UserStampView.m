//
//  UserStampView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "UserStampView.h"

@implementation UserStampView
@synthesize size;

- (id)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        self.size = STStampImageSize14;
        self.backgroundColor = [UIColor clearColor];
    }
    return self;    
}

- (void)dealloc {
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);
    CGContextClipToMask(ctx, rect, [UIImage imageNamed:[NSString stringWithFormat:@"stamp_%dpt_texture.png", self.size]].CGImage);
    
    if (self.highlighted) {
        
        [[UIColor whiteColor] setFill];
        CGContextFillRect(ctx, rect);
        
    } else {
        
        CGRect rect = CGContextGetClipBoundingBox(ctx);
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
        
    }
    
}


#pragma mark - View Setup

- (void)setupWithUser:(id<STUser>)user {
   
    [Util splitHexString:user.primaryColor toRed:&r green:&g blue:&b];
    [Util splitHexString:user.secondaryColor toRed:&r1 green:&g1 blue:&b1]; 
    [self setNeedsDisplay];
    
}

- (void)setupWithColors:(NSArray*)colors {
    if (!colors || [colors count] < 2) return; // invalid colors

    const CGFloat *top = CGColorGetComponents([[colors objectAtIndex:0] CGColor]);
    const CGFloat *bottom = CGColorGetComponents([[colors objectAtIndex:1] CGColor]);
    
    r = top[0];
    g = top[1];
    b = top[2];
    
    r1 = bottom[0];
    g1 = bottom[1];
    b1 = bottom[2];

    [self setNeedsDisplay];

}


#pragma mark - Setters

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [self setNeedsDisplay];
}


#pragma mark - Getters

- (NSArray*)colors {
    
    return [NSArray arrayWithObjects:[UIColor colorWithRed:r green:g blue:b alpha:1.0f], [UIColor colorWithRed:r1 green:g1 blue:b1 alpha:1.0f], nil];
    
}

@end
