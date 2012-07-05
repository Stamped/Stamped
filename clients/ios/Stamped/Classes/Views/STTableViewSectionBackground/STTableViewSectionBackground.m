//
//  STTableViewSectionBackground.m
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import "STTableViewSectionBackground.h"
#import "QuartzUtils.h"

@implementation STTableViewSectionBackground

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.userInteractionEnabled = NO;
        self.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.backgroundColor = [UIColor clearColor];
    }
    return self;
}

- (void)drawRect:(CGRect)rect {

    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGFloat inset = 6.0f;
    CGFloat corner = 2.0f;
    
    UIColor *bottomColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:0.6f];
    UIColor *topColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.8f];
    
    CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, inset, 2) cornerRadius:corner].CGPath;
    
    // drop shadow
    CGContextSaveGState(ctx);
    CGContextSetFillColorWithColor(ctx, [UIColor whiteColor].CGColor);
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 2.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.05].CGColor);
    CGContextAddPath(ctx, path);
    CGContextFillPath(ctx);
    CGContextAddPath(ctx, path);
    CGContextClip(ctx);
    CGContextClearRect(ctx, rect);
    CGContextRestoreGState(ctx);
    
    // gradient fill
    CGContextSaveGState(ctx);
    CGContextAddPath(ctx, path);
    CGContextClip(ctx);
    drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);

    // inner shadow
    CGFloat originY = 2.0f;
    CGFloat originX = inset;
    CGContextSetStrokeColorWithColor(ctx, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.4f].CGColor);
    CGContextMoveToPoint(ctx, originX, originY + corner);
    CGContextAddQuadCurveToPoint(ctx, originX, originY, originX + corner, originY);
    CGContextAddLineToPoint(ctx, rect.size.width-(originX+corner), originY);
    CGContextAddQuadCurveToPoint(ctx, rect.size.width-originX, originY, rect.size.width-originX, originY + corner);
    CGContextStrokePath(ctx);
    CGContextRestoreGState(ctx);
    
    // gradient stroke
    bottomColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:0.6f];
    topColor = [UIColor colorWithRed:0.8f green:0.8f blue:0.8f alpha:0.8f];
    CGContextAddPath(ctx, path);
    CGContextReplacePathWithStrokedPath(ctx);
    CGContextClip(ctx);
    drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
    
    
}

@end
