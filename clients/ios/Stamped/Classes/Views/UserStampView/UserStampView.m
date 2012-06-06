//
//  UserStampView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "UserStampView.h"

@implementation UserStampView
@synthesize highlighted=_highlighted;
@synthesize size;

- (id)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        self.size = STStampImageSize14;
        self.backgroundColor = [UIColor clearColor];
    }
    return self;    
}

- (void)dealloc {
    
    /*
    if (_color1) {
        [_color1 release], _color1=nil;
    }
    
    if (_color2) {
        [_color2 release], _color2=nil;
    }
    */
    
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
        
        /*
        if (_color1 && _color2) {
            
            drawStampGradient([_color1 CGColor], [_color2 CGColor], ctx);
        } else {
            CGContextFillRect(ctx, rect);
        }
         */
        
    }
    
}


#pragma mark - View Setup

- (void)setupWithUser:(id<STUser>)user {
   
    //float r,g,b;
    [Util splitHexString:user.primaryColor toRed:&r green:&g blue:&b];
    //[_color1 release], _color1=nil;
    //_color1 = [[UIColor colorWithRed:r green:g blue:b alpha:1.0f] retain];
    
    [Util splitHexString:user.secondaryColor toRed:&r1 green:&g1 blue:&b1];
    //[_color2 release], _color2=nil;
    //_color2 = [[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:1.0f] retain];
 
    [self setNeedsDisplay];
    
}

- (void)setupWithColors:(NSArray*)colors {
    /*
    if (!colors || [colors count] < 2) return;
    
    [_color1 release], _color1=nil;
    _color1 = [[colors objectAtIndex:0] retain];
    
    [_color2 release], _color2=nil;
    _color2 = [[colors objectAtIndex:1] retain];
     */
    
    [self setNeedsDisplay];

}


#pragma mark - Setters

- (void)setHighlighted:(BOOL)highlighted {
    _highlighted = highlighted;
    [self setNeedsDisplay];
}

@end
