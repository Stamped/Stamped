//
//  STTextPopoverView.m
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import "STTextPopoverView.h"
#import "QuartzUtils.h"
#import "STAppDelegate.h"

#define CALLOUT_HEIGHT 50
#define OUT_ANIMATION_DURATION 0.2f
#define IN_ANIMATION_DURATION .25f

#define kPopoverCornerRadius 4
#define kPopoverShadowRadius 3
#define kPopoverArrowHeight 6
#define kPopoverArrowWidth 12

@implementation STTextPopoverView

@synthesize title=_title;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor clearColor];
        self.alpha = 0.95f;
    }
    return self;
}

- (void)dealloc {
	[_title release], _title=nil;
    [super dealloc];
}


#pragma mark - Drawing

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    rect = CGRectInset(rect, kPopoverShadowRadius, kPopoverShadowRadius);
    rect.size.height -= 2.0f;
    
    CGFloat minX = rect.origin.x;
    CGFloat minY = rect.origin.y;
    CGFloat maxX = rect.origin.x + rect.size.width;
    CGFloat maxY = rect.origin.y + rect.size.height;
    
    maxY -= kPopoverArrowHeight; 
    
    CGContextSaveGState(ctx);
    CGMutablePathRef _path = CGPathCreateMutable();
    
    // top left
    CGPathMoveToPoint(_path, NULL, minX, minY+kPopoverCornerRadius);
    CGPathAddQuadCurveToPoint(_path, NULL, minX, minY, minX+kPopoverCornerRadius, minY);
    
    // top right
    CGPathAddLineToPoint(_path, NULL, maxX-kPopoverCornerRadius, minY);
    CGPathAddQuadCurveToPoint(_path, NULL, maxX, minY, maxX, minY+kPopoverCornerRadius);
    CGPathAddLineToPoint(_path, NULL, maxX, maxY-kPopoverCornerRadius);
    
    // bottom right
    CGPathAddQuadCurveToPoint(_path, NULL, maxX, maxY, maxX-kPopoverCornerRadius, maxY);
    
    CGPathAddLineToPoint(_path, NULL, _arrowLocation + (kPopoverArrowWidth/2), maxY);
    CGPathAddLineToPoint(_path, NULL, _arrowLocation, maxY + kPopoverArrowHeight);
    CGPathAddLineToPoint(_path, NULL, _arrowLocation - (kPopoverArrowWidth/2), maxY);
    
    CGPathAddLineToPoint(_path, NULL, minX+kPopoverCornerRadius, maxY);
    
    // bottom left
    CGPathAddQuadCurveToPoint(_path, NULL, minX, maxY, minX, maxY-kPopoverCornerRadius);
    CGPathAddLineToPoint(_path, NULL, minX, minY+kPopoverCornerRadius);
    
    CGContextSaveGState(ctx);
    CGContextSetShadowWithColor(ctx, CGSizeMake(0, 1), 3, [UIColor blackColor].CGColor);
    [[UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f] setStroke];
    CGContextAddPath(ctx, _path);
    CGContextStrokePath(ctx);
    CGContextSetShadow(ctx, CGSizeZero, 0);
    CGContextRestoreGState(ctx);
    
    CGContextAddPath(ctx, _path);
    CGContextClip(ctx);
    
    drawGradient([UIColor colorWithRed:0.369f green:0.369f blue:0.369f alpha:1.0f].CGColor, [UIColor colorWithRed:0.1960 green:0.1960 blue:0.1960 alpha:1.0f].CGColor, ctx);
    CGContextRestoreGState(ctx);
    
    
    // second arrow line
    if (_arrowLocation!=0) {
        
        CGContextSaveGState(ctx);
        
        minY = ceilf(minY+1);
        
        CGMutablePathRef _secondPath = CGPathCreateMutable();
        [[UIColor colorWithRed:0.439f green:0.439f blue:0.439f alpha:1.0f] setStroke];
        
        CGPathMoveToPoint(_secondPath, NULL, minX, minY+kPopoverCornerRadius);
        CGPathAddQuadCurveToPoint(_secondPath, NULL, minX, minY, minX+kPopoverCornerRadius, minY);
        CGPathAddLineToPoint(_secondPath, NULL, maxX-kPopoverCornerRadius, minY);
        CGPathAddQuadCurveToPoint(_secondPath, NULL, maxX, minY, maxX, minY+kPopoverCornerRadius);
        
        CGContextAddPath(ctx, _secondPath);
        CGContextStrokePath(ctx);
        CGPathRelease(_secondPath);
        CGContextRestoreGState(ctx);
        
    }
    
    if (_title) {
		[[UIColor whiteColor] setFill];
        CGContextSetShadowWithColor(ctx, CGSizeMake(0, -1), 0, [UIColor colorWithRed:0.173f green:0.173f blue:0.173f alpha:1.0f].CGColor);
		[_title drawInRect:CGRectMake(4, 13.0f, self.frame.size.width-8, 24) withFont:[UIFont boldSystemFontOfSize:12] lineBreakMode:UILineBreakModeMiddleTruncation alignment:UITextAlignmentCenter];
	}
    
    CGContextAddPath(ctx, _path);
    CGContextReplacePathWithStrokedPath(ctx);
    CGContextClip(ctx);
    drawGradient([UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f].CGColor, [UIColor colorWithRed:0.153f green:0.153f blue:0.153f alpha:1.0f].CGColor, ctx);
    CGPathRelease(_path);

}


#pragma mark - Animations

- (CAAnimationGroup*)inAnimation {
	
	CAAnimationGroup *animation = [CAAnimationGroup animation];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut];
	
	CAKeyframeAnimation *scaleAnimation = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
	scaleAnimation.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.01f],
                             //[NSNumber numberWithFloat:1.1f],
                             [NSNumber numberWithFloat:1.0f], nil];
    
    CGPoint fromPos = self.layer.position;
    fromPos.y += 4.0f;
    CABasicAnimation *position = [CABasicAnimation animationWithKeyPath:@"position"];
    position.fromValue = [NSValue valueWithCGPoint:fromPos];
    //position.toValue = [NSValue valueWithCGPoint:self.layer.position];
    
    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:0.0f];
    
	animation.duration = 0.2f;
	animation.animations = [NSArray arrayWithObjects:position, opacity, scaleAnimation, nil];
	
	return animation;
	
}

- (CAAnimationGroup*)outAnimation {
	
	CAAnimationGroup *animation = [CAAnimationGroup animation];
    
	CABasicAnimation *scaleAnimation = [CABasicAnimation animationWithKeyPath:@"transform"];
	scaleAnimation.toValue = [NSValue valueWithCATransform3D:CATransform3DMakeScale(0.01f, 0.01f, 1.0f)];
	
	CABasicAnimation *posAnimation = [CABasicAnimation animationWithKeyPath:@"position"];
	posAnimation.toValue = [NSValue valueWithCGPoint:CGPointMake(self.layer.position.x, self.layer.position.y + self.frame.size.height/3)];
	
    CABasicAnimation *opacityAnimation = [CABasicAnimation animationWithKeyPath:@"opacity"];
	opacityAnimation.toValue = [NSNumber numberWithFloat:0.0f];

	animation.removedOnCompletion = NO;
	animation.fillMode = kCAFillModeForwards;
	animation.delegate = self;
	animation.duration = OUT_ANIMATION_DURATION;
	animation.animations = [NSArray arrayWithObjects:scaleAnimation, posAnimation, opacityAnimation, nil];
	
	return animation;
	
}


#pragma mark - Presentation

- (void)animationDidStop:(CAAnimation *)anim finished:(BOOL)flag {
	
	if (flag) {
		[self removeFromSuperview];
	}
}

- (void)showFromView:(UIView*)view position:(CGPoint)point animated:(BOOL)animated {
    
    if (!self.superview) {
        
        // no superview, add to main view controller
        UIView *view = [((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController view];
        [view addSubview:self];
        
    }
    
    point = [view convertPoint:point toView:self.superview];
    
	CGFloat width = 0.0f;
	if (_title) {
		width = MIN(300, [_title sizeWithFont:[UIFont boldSystemFontOfSize:14]].width + 30.0f);
	}
    
    _arrowLocation = (width/2);
    
    CGRect frame = CGRectZero;
    if (self.superview && [self.superview isKindOfClass:[UIScrollView class]]) {
        
        UIScrollView *scrollView = (UIScrollView*)self.superview;
        
        CGFloat diff = 0;
        CGFloat maxScroll = (scrollView.contentOffset.x + scrollView.frame.size.width);
        frame = CGRectMake(floorf(point.x - (width/2)), floorf(point.y - (CALLOUT_HEIGHT - 15)), width, CALLOUT_HEIGHT);
        if (frame.origin.x < (scrollView.contentOffset.x-34)) {
            
            diff = ((scrollView.contentOffset.x-34) - frame.origin.x);
            _arrowLocation = (frame.size.width/2) - diff;
            frame.origin.x = scrollView.contentOffset.x-34;
            
        } else if (CGRectGetMaxX(frame) > (maxScroll+34)) {
            
            diff = ((maxScroll+34) - CGRectGetMaxX(frame));
            _arrowLocation = (frame.size.width/2) - diff;
            frame.origin.x = (maxScroll+34) - frame.size.width;
            
        } else {
            _arrowLocation = (frame.size.width/2);
        }
        
    } else {
        frame = CGRectMake(floorf(point.x - (width/2)), floorf(point.y - (CALLOUT_HEIGHT - 15)), width, CALLOUT_HEIGHT);
        _arrowLocation = (frame.size.width/2);
    }
    
    
    if (frame.origin.x < 10.0f) {
        
        CGFloat diff = (10.0f - frame.origin.x);
        frame.origin.x = 10.0f;
        _arrowLocation = floorf(_arrowLocation - diff);
        
    }
    
    CGFloat maxWidth  = ([[UIScreen mainScreen] applicationFrame].size.width-(frame.size.width+10.0f));
    if (frame.origin.x > maxWidth) {
        
        CGFloat diff = (maxWidth - frame.origin.x);
        frame.origin.x = maxWidth;
        _arrowLocation = floorf(_arrowLocation - diff);
        
    }
    
	self.frame = frame;
	
	if (animated) {
		[self.layer addAnimation:[self inAnimation] forKey:nil];
	}
	
	[self setNeedsDisplay];
    
}

- (void)hide {
	[self.layer addAnimation:[self outAnimation] forKey:@"DropOutAnimation"];	
}

- (void)hideDelayed:(float)delay {
    
    CAAnimationGroup *animation = [self outAnimation];
    animation.beginTime = [self.layer convertTime:CACurrentMediaTime() fromLayer:nil] + delay;
	[self.layer addAnimation:animation forKey:@"DropOutAnimation"];	
    
}


@end
