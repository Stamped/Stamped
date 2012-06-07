//
//  STDetailTextCallout.m
//  Stamped
//
//  Created by Devin Doty on 5/29/12.
//
//

#import "STDetailTextCallout.h"

#define kPopoverCornerRadius 6
#define kPopoverShadowRadius 1
#define kPopoverArrowHeight 10
#define kPopoverArrowWidth 30

#define kLabelGap 2.0
#define kAnimationDuration .2

@implementation STDetailTextCallout

@synthesize titleLabel=_titleLabel;
@synthesize subTitleLabel=_subTitleLabel;
@synthesize detailTitleLabel=_detailTitleLabel;
@synthesize sticky;
@synthesize completion;

@synthesize arrowDirection=_arrowDirection;

- (id)initWithFrame:(CGRect)frame arrowDirection:(STDetailTextCalloutArrowDirection)direction {
    if ((self = [super initWithFrame:frame])) {
        _arrowDirection = direction;
        self.backgroundColor = [UIColor clearColor];
    }
    return self;
}

- (id)initWithFrame:(CGRect)frame {
    return [self initWithFrame:frame arrowDirection:STDetailTextCalloutArrowDirectionDown];
}

- (UILabel*)titleLabel {
    
    if (_titleLabel==nil) {
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont boldSystemFontOfSize:16];
        label.textColor = [UIColor whiteColor];
        label.lineBreakMode = UILineBreakModeWordWrap;
        [self addSubview:label];
        _titleLabel = label;
        [label release];
        
    }
    
    return _titleLabel;
    
}

- (UILabel*)detailTitleLabel {
    
    if (_detailTitleLabel==nil) {
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor whiteColor];
        label.font = [UIFont systemFontOfSize:15];
        label.backgroundColor = [UIColor clearColor];
        label.lineBreakMode = UILineBreakModeWordWrap;
        [self addSubview:label];
        _detailTitleLabel = label;
        [label release];
        
    }
    
    return _detailTitleLabel;
    
}

- (UILabel*)subTitleLabel {
    
    if (_subTitleLabel==nil) {
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithWhite:.95 alpha:1.0];
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = [UIColor clearColor];
        label.lineBreakMode = UILineBreakModeTailTruncation;
        [self addSubview:label];
        _subTitleLabel = label;
        [label release];
        
    }
    
    return _subTitleLabel;
    
}

- (void)fadeIn {
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"opacity"];
    animation.fromValue = [NSNumber numberWithFloat:0.0];
    animation.toValue = [NSNumber numberWithFloat:1.0];
    animation.duration = kAnimationDuration;
    [self.layer addAnimation:animation forKey:@"fade_animation"];
    
}

- (void)fadeOut {
    
    __block STDetailTextCallout *selfRef = self;
    [CATransaction begin];
    [CATransaction setAnimationDuration:kAnimationDuration];
    [CATransaction setCompletionBlock:^{
        [selfRef removeFromSuperview];
    }];
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"opacity"];
    animation.duration = kAnimationDuration;
    animation.fromValue = [NSNumber numberWithFloat:1.0];
    animation.toValue = [NSNumber numberWithFloat:0.0];
    animation.removedOnCompletion = NO;
    animation.fillMode = kCAFillModeForwards;
    [self.layer addAnimation:animation forKey:@"fade_animation"];
    
    [CATransaction commit];
    
}

- (void)showCalloutFromRect:(CGRect)rect animated:(BOOL)animated autoArrowDirection:(BOOL)autoArrowDirection {

	CGSize layoutSize = CGSizeZero;
    CGFloat originX = 12;
    CGFloat originY = 7;
    CGFloat maxWidth = [[UIScreen mainScreen] applicationFrame].size.width - 30;
    CGFloat maxLabelWidth = maxWidth - 8;
	
	CGFloat arrowYOffset = _arrowDirection == STDetailTextCalloutArrowDirectionUp ? kPopoverArrowHeight : 0.0f;
    
    if (_titleLabel && _titleLabel.text) {
        
        CGSize size = [_titleLabel.text sizeWithFont:_titleLabel.font constrainedToSize:CGSizeMake(maxLabelWidth, CGFLOAT_MAX)];

        _titleLabel.frame = CGRectMake(originX, originY + arrowYOffset, size.width, size.height);
        _titleLabel.numberOfLines = (size.height / _titleLabel.font.lineHeight);
        
        layoutSize.height += (size.height+kLabelGap);
        layoutSize.width = MAX(layoutSize.width, size.width);
        
	}
    
    if (_detailTitleLabel && _detailTitleLabel.text) {
        
        CGSize size = [_detailTitleLabel.text sizeWithFont:_detailTitleLabel.font constrainedToSize:CGSizeMake(maxLabelWidth, CGFLOAT_MAX)];

        _detailTitleLabel.frame = CGRectMake(originX, originY + layoutSize.height + arrowYOffset, size.width, size.height);
        _detailTitleLabel.numberOfLines = (size.height / _detailTitleLabel.font.lineHeight);
        
        layoutSize.height += (size.height+kLabelGap);
        layoutSize.width = MAX(layoutSize.width, size.width);
        
    }
    
    if (_subTitleLabel && _subTitleLabel.text) {
        
        CGSize size = [_subTitleLabel.text sizeWithFont:_subTitleLabel.font];

        _subTitleLabel.frame = CGRectMake(originX, originY + layoutSize.height + arrowYOffset, size.width, size.height);
        
        layoutSize.height += (size.height+kLabelGap);
        layoutSize.width = MAX(layoutSize.width, size.width);
        
    }

    layoutSize.width += 24;
    layoutSize.height += 24;
    
    CGRect frame = CGRectZero;
    if (self.superview) {
        
        UIView *view = self.superview;
        
        CGFloat diff = 0;
		CGPoint point = rect.origin;

		if(autoArrowDirection) {
			if(floorf(point.y - layoutSize.height) < 10.0f) {
				if(_arrowDirection != STDetailTextCalloutArrowDirectionUp) {
					CGRect rect = _titleLabel.frame;
					rect.origin.y += kPopoverArrowHeight;
					_titleLabel.frame = rect;
					
					rect = _detailTitleLabel.frame;
					rect.origin.y += kPopoverArrowHeight;
					_detailTitleLabel.frame = rect;
					
					rect = _subTitleLabel.frame;
					rect.origin.y += kPopoverArrowHeight;
					_subTitleLabel.frame = rect;
				}
				
				_arrowDirection = STDetailTextCalloutArrowDirectionUp;
				point.y = CGRectGetMaxY(rect);
			} else if(_arrowDirection != STDetailTextCalloutArrowDirectionDown) {
				CGRect rect = _titleLabel.frame;
				rect.origin.y -= kPopoverArrowHeight;
				_titleLabel.frame = rect;
				
				rect = _detailTitleLabel.frame;
				rect.origin.y -= kPopoverArrowHeight;
				_detailTitleLabel.frame = rect;
				
				rect = _subTitleLabel.frame;
				rect.origin.y -= kPopoverArrowHeight;
				_subTitleLabel.frame = rect;

				_arrowDirection = STDetailTextCalloutArrowDirectionDown;
			}
		}
		
		if(_arrowDirection == STDetailTextCalloutArrowDirectionUp) {
			frame = CGRectMake(floorf(point.x - (layoutSize.width/2)), floorf(point.y), layoutSize.width, layoutSize.height);
		} else {
			frame = CGRectMake(floorf(point.x - (layoutSize.width/2)), floorf(point.y - layoutSize.height), layoutSize.width, layoutSize.height);
		}

        if (frame.origin.x < (view.frame.origin.x+14)) {
            
            diff = ((view.frame.origin.x+14) - frame.origin.x);
            _arrowLocation = (frame.size.width/2) - diff;
            frame.origin.x = (view.frame.origin.x+14);
            
        } else if (CGRectGetMaxX(frame) > (view.frame.size.width-14)) {
            
            diff = ((view.frame.size.width-14) - CGRectGetMaxX(frame));
            _arrowLocation = (frame.size.width/2) - diff;
            frame.origin.x = (view.frame.size.width-14) - frame.size.width;
            
        } else {
            _arrowLocation = (frame.size.width/2);
        }
        
        _arrowLocation = MIN(_arrowLocation, frame.size.width - 20);
        _arrowLocation = MAX(20, _arrowLocation);
        
    } 
    
	self.frame = frame;
	
	if (animated) {
        [self fadeIn];
	}
	
	[self setNeedsDisplay];
    
}

- (void)showCalloutFromRect:(CGRect)rect animated:(BOOL)animated {
	[self showCalloutFromRect:rect animated:animated autoArrowDirection:YES];
}

- (void)showCalloutFromPoint:(CGPoint)point animated:(BOOL)animated {
	[self showCalloutFromRect:CGRectMake(point.x, point.y, 1.0f, 1.0f) animated:animated autoArrowDirection:NO];
}

- (void)hide {
        
    [self fadeOut];

}

- (void)hideDelayed:(float)delay {
    
    double delayInSeconds = delay;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [self fadeOut];
    });
    
}

- (CGMutablePathRef)createCalloutPathInRect:(CGRect)rect {
    
    CGFloat minX = rect.origin.x;
    CGFloat minY = rect.origin.y;
    CGFloat maxX = rect.origin.x + rect.size.width;
    CGFloat maxY = rect.origin.y + rect.size.height;
    
    CGMutablePathRef _path = CGPathCreateMutable();
	
	if(_arrowDirection == STDetailTextCalloutArrowDirectionUp) {
		minY += kPopoverArrowHeight; 
	} else {
		maxY -= kPopoverArrowHeight; 
	}
    
    // top left
    CGPathMoveToPoint(_path, NULL, minX, minY+kPopoverCornerRadius);
    CGPathAddQuadCurveToPoint(_path, NULL, minX, minY, minX+kPopoverCornerRadius, minY);
	
	if(_arrowDirection == STDetailTextCalloutArrowDirectionUp) {
		CGPathAddLineToPoint(_path, NULL, _arrowLocation + (kPopoverArrowWidth/2), minY);
		CGPathAddLineToPoint(_path, NULL, _arrowLocation, minY - kPopoverArrowHeight);
		CGPathAddLineToPoint(_path, NULL, _arrowLocation - (kPopoverArrowWidth/2), minY);
	}
    
    // top right
    CGPathAddLineToPoint(_path, NULL, maxX-kPopoverCornerRadius, minY);
    CGPathAddQuadCurveToPoint(_path, NULL, maxX, minY, maxX, minY+kPopoverCornerRadius);
    CGPathAddLineToPoint(_path, NULL, maxX, maxY-kPopoverCornerRadius);
    
    // bottom right
    CGPathAddQuadCurveToPoint(_path, NULL, maxX, maxY, maxX-kPopoverCornerRadius, maxY);
    
	if(_arrowDirection == STDetailTextCalloutArrowDirectionDown) {
		CGPathAddLineToPoint(_path, NULL, _arrowLocation + (kPopoverArrowWidth/2), maxY);
		CGPathAddLineToPoint(_path, NULL, _arrowLocation, maxY + kPopoverArrowHeight);
		CGPathAddLineToPoint(_path, NULL, _arrowLocation - (kPopoverArrowWidth/2), maxY);
	}
    
    CGPathAddLineToPoint(_path, NULL, minX+kPopoverCornerRadius, maxY);
    
    // bottom left
    CGPathAddQuadCurveToPoint(_path, NULL, minX, maxY, minX, maxY-kPopoverCornerRadius);
    CGPathAddLineToPoint(_path, NULL, minX, minY+kPopoverCornerRadius);
    
    return _path;
    
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    rect = CGRectInset(rect, kPopoverShadowRadius, kPopoverShadowRadius);
    
    CGMutablePathRef _path = [self createCalloutPathInRect:rect];
	
	CGFloat minX = rect.origin.x;
	CGFloat minY = rect.origin.y;
	CGFloat maxX = rect.origin.x + rect.size.width;

	if (_arrowLocation!=0) {
		if(_arrowDirection == STDetailTextCalloutArrowDirectionUp) {
			minY += kPopoverArrowHeight; 
		} 
	}

    // fill 
    CGContextAddPath(ctx, _path);
    [[UIColor colorWithRed:0.188f green:0.188f blue:0.188f alpha:1.0f] setFill];
    CGContextFillPath(ctx);
    
    // bubble
    CGContextSaveGState(ctx);
    CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:CGRectMake(rect.origin.x + .5, minY + 1, rect.size.width-1, 26) cornerRadius:kPopoverCornerRadius].CGPath);
    CGContextClip(ctx);
    drawGradient([UIColor colorWithRed:0.400f green:0.400f blue:0.400f alpha:1.0f].CGColor, [UIColor colorWithRed:0.259f green:0.259f blue:0.259f alpha:1.0f].CGColor, ctx);
    CGContextRestoreGState(ctx);
    
    
    // second arrow line
    if (_arrowLocation!=0) {

        CGContextSaveGState(ctx);
        
        minY = ceilf(minY+1);
        
        CGMutablePathRef _secondPath = CGPathCreateMutable();
        [[UIColor colorWithRed:1 green:1 blue:1 alpha:.4] setStroke];
        
		
		CGPathMoveToPoint(_secondPath, NULL, minX, minY+kPopoverCornerRadius);
		CGPathAddQuadCurveToPoint(_secondPath, NULL, minX, minY, minX+kPopoverCornerRadius, minY);
		CGPathAddLineToPoint(_secondPath, NULL, maxX-kPopoverCornerRadius, minY);
		CGPathAddQuadCurveToPoint(_secondPath, NULL, maxX, minY, maxX, minY+kPopoverCornerRadius);
        
        CGContextAddPath(ctx, _secondPath);
        CGContextStrokePath(ctx);
        CGPathRelease(_secondPath);
        CGContextRestoreGState(ctx);
        
    }
    
    // outter stroke
    [[UIColor colorWithRed:0.310f green:0.310f blue:0.310f alpha:1.0f] setStroke];
    CGContextAddPath(ctx, _path);
    CGContextStrokePath(ctx);
    CGPathRelease(_path);
    
    // inner stroke
    _path = [self createCalloutPathInRect:CGRectInset(rect, 1.0, 1.0)];
    [[UIColor colorWithRed:1 green:1 blue:1 alpha:.1] setStroke];
    CGContextAddPath(ctx, _path);
    CGContextStrokePath(ctx);
    CGPathRelease(_path);

}

- (void)dealloc {
    
    _detailTitleLabel=nil;
    _subTitleLabel=nil;
    _titleLabel=nil;
    
    [super dealloc];
}

@end