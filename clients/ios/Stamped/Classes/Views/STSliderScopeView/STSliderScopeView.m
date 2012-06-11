//
//  STSliderScopeView.m
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import "STSliderScopeView.h"
#import "STTextPopoverView.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STImageCache.h"
#import "STTextCalloutView.h"

#define kSliderTrackGap 76
#define kSliderTwoTrackGap 50

@interface STSliderScopeView (Internal)
- (UIImageView*)imageViewForScope:(STStampedAPIScope)scope;
- (void)setUserImageViewImage:(UIImage*)image;


@end

@interface STSliderScopeView ()


@property (nonatomic, readwrite, retain) NSTimer* timer;

@end

@implementation STSliderScopeView
@synthesize scope=_scope;
@synthesize longPress=_longPress;
@synthesize delegate;
@synthesize dataSource;
@synthesize selectedIndex=_selectedIndex;
@synthesize timer = _timer;

- (void)commonInit {
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [self addSubview:background];
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
        
        [[UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:1.0f] setFill];
        CGContextFillRect(ctx, rect);
        
        CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect byRoundingCorners:(UIRectCornerBottomLeft | UIRectCornerBottomRight) cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath);
        CGContextClip(ctx);
        
        drawGradient([UIColor colorWithRed:0.345f green:0.345f blue:0.345f alpha:1.0f].CGColor, [UIColor colorWithRed:0.1529f green:0.1529f blue:0.1529f alpha:1.0f].CGColor, ctx);
        
        CGContextMoveToPoint(ctx, 0.0f, 0.5f);
        CGContextAddLineToPoint(ctx, rect.size.width, 0.5f);
        [[UIColor colorWithRed:0.286f green:0.286f blue:0.286f alpha:1.0f] setStroke];
        CGContextStrokePath(ctx);
        
        CGContextMoveToPoint(ctx, 0.0f, 1.5f);
        CGContextAddLineToPoint(ctx, rect.size.width, 1.5f);
        [[UIColor colorWithRed:0.416f green:0.416f blue:0.416f alpha:1.0f] setStroke];
        CGContextStrokePath(ctx);
        
    }];
    [background release];
    
    UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tap:)];
    tap.delegate = (id<UIGestureRecognizerDelegate>)self;
    [self addGestureRecognizer:tap];
    [tap release];
    
    UILongPressGestureRecognizer *gesture = [[UILongPressGestureRecognizer alloc] initWithTarget:self action:@selector(press:)];
    gesture.minimumPressDuration = 0.5f;
    [self addGestureRecognizer:gesture];
    _longPress = gesture;
    [gesture release];
    
    UIPanGestureRecognizer *pan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(pan:)];
    pan.delegate = (id<UIGestureRecognizerDelegate>)self;
    [self addGestureRecognizer:pan];
    [pan release];
    
    UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:(_style == STSliderScopeStyleTwo) ? @"slider_track_2.png" : @"slider_track_3.png"]];
    view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
    [self addSubview:view];
    CGRect frame = view.frame;
    frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
    frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
    view.frame = frame;
    [view release];
    
    UIImageView *imageView = [[UIImageView alloc] initWithImage:[self imageForScope:0]];
    [self addSubview:imageView];
    _draggingView = imageView;
    [imageView release];
    
    self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
    self.layer.shadowOpacity = 1;
    self.layer.shadowOffset = CGSizeMake(0, -1);

    id<STUser> user = STStampedAPI.sharedInstance.currentUser;
    if (user) {
        
        UIImage *image = [[STImageCache sharedInstance] cachedUserImageForUser:user size:STProfileImageSize46];
        if (image) {
            
            [self setUserImageViewImage:image];
            
        } else {
            
            [[STImageCache sharedInstance] userImageForUser:(id<STUser>)user size:STProfileImageSize46 andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                [self setUserImageViewImage:image];
            }];
            
        }
    }
    
}

- (id)initWithStyle:(STSliderScopeStyle)style frame:(CGRect)frame {    
    if ((self = [super initWithFrame:frame])) {
        _style = style;
        [self commonInit];
    }
    return self;
}

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        _style = STSliderScopeStyleThree;
        [self commonInit];
    }
    return self;
}

- (void)dealloc {
    if (_userImage) {
        [_userImage release], _userImage = nil;
    }
    [_timer invalidate];
    [_timer release];
    _textCallout = nil;
    [super dealloc];
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    _draggingView.layer.position = [self positionForScope:_scope];
    
    
}

- (CGPoint)positionForScope:(STStampedAPIScope)scope {

    CGPoint pos = CGPointMake(floorf(self.bounds.size.width/2), floorf(self.bounds.size.height/2) + 1.0f);
    
    switch (scope) {
        case STStampedAPIScopeYou:
            pos.x = ((self.bounds.size.width/2) - ((_style == STSliderScopeStyleTwo) ? kSliderTwoTrackGap : kSliderTrackGap));
            break;
        case STStampedAPIScopeFriends:
            pos.x = (self.bounds.size.width/2);
            break;
        case STStampedAPIScopeEveryone:
            pos.x = _style == STSliderScopeStyleTwo ? ((self.bounds.size.width/2) + kSliderTwoTrackGap) : ((self.bounds.size.width/2) + kSliderTrackGap);
            break;
        default:
            break;
    }
    
    return pos;
    
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope animated:(BOOL)animated {
    _scope = scope;
    
    if (!_dragging) {
        _draggingView.layer.position = [self positionForScope:_scope];
        _draggingView.image = [self imageForScope:_scope];
    }

}

- (void)setScope:(STStampedAPIScope)scope {
    [self setScope:scope animated:NO];
}

- (void)setScopeExplicit:(STStampedAPIScope)scope {
    [self setScope:scope];
    
    if ([(id)delegate respondsToSelector:@selector(sliderScopeView:didChangeScope:)]) {
        [self.delegate sliderScopeView:self didChangeScope:scope];
    }
    
}

- (void)setUserImageViewImage:(UIImage*)image {
    
    if (image) {
        
        UIImage *overlay = [UIImage imageNamed:@"scope_drag_inner_avatar.png"];
        UIGraphicsBeginImageContextWithOptions(overlay.size, NO, 0);
        CGContextRef ctx = UIGraphicsGetCurrentContext();
        CGRect rect = CGContextGetClipBoundingBox(ctx);
        rect.origin.y = 6.0f;
        rect.origin.x = (rect.size.width-28.0f)/2;
        rect.size =  CGSizeMake(28, 28);
    
        CGContextSaveGState(ctx);
        CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:14.0f].CGPath;
        CGContextAddPath(ctx, path);
        CGContextClip(ctx);
        [image drawInRect:rect];
        CGContextRestoreGState(ctx);
        [overlay drawAtPoint:CGPointZero];

        _userImage = [UIGraphicsGetImageFromCurrentImageContext() retain];        
        UIGraphicsEndImageContext();
        
        if (self.scope == STStampedAPIScopeYou) {
            _draggingView.image = _userImage;
        }
        
    }
    
}


#pragma mark - Getters (Internal)

- (UIView*)viewForScope:(STStampedAPIScope)scope {
    
    return [self viewWithTag:(scope+1)*100];
    
}
    
- (NSString*)titleForScope:(STStampedAPIScope)scope {
    
    if ([(id)dataSource respondsToSelector:@selector(sliderScopeView:titleForScope:)]) {
        return [self.dataSource sliderScopeView:self titleForScope:scope];
    } 
    
    NSString *string = nil;
    switch (scope) {
        case STStampedAPIScopeYou:
            string = NSLocalizedString(@"you", @"you");
            break;
        case STStampedAPIScopeFriends:
            string = NSLocalizedString(@"you + friends", @"you + friends");
            break;
        case STStampedAPIScopeEveryone:
            string = NSLocalizedString(@"tastemakers", @"tastemakers");
            break;
        default:
            break;
    }
    
    return string;
    
}

- (NSString*)boldTitleForScope:(STStampedAPIScope)scope {
    
    if ([(id)dataSource respondsToSelector:@selector(sliderScopeView:boldTitleForScope:)]) {
        return [self.dataSource sliderScopeView:self boldTitleForScope:scope];
    } 
    
    return [self titleForScope:scope];
    
}

- (STStampedAPIScope)scopeForPosition:(CGPoint)position {

    if (_style == STSliderScopeStyleTwo) {
        
        if (position.x < (self.bounds.size.width/2)) {
            return STStampedAPIScopeYou;
        }
        
    } else {
        
        CGFloat xOrigin = (self.bounds.size.width-60.0f)/2;
        CGRect rect = CGRectMake(xOrigin, 0.0f, 60.0f, self.bounds.size.height);
        if (CGRectContainsPoint(rect, position)) {
            return STStampedAPIScopeFriends;
        } else if (position.x < xOrigin) {
            return STStampedAPIScopeYou;
        }
        
    }


    return STStampedAPIScopeEveryone; // defaults to you

}

- (UIImage*)imageForScope:(STStampedAPIScope)scope  {
    
    UIImage *image = nil;
    switch (scope) {
        case STStampedAPIScopeYou:
            image = (_userImage== nil) ? [UIImage imageNamed:@"scope_drag_inner_you.png"] : _userImage;
            break;
        case STStampedAPIScopeFriends:
            image = [UIImage imageNamed:@"scope_drag_inner_friends.png"];
            break;
        case STStampedAPIScopeFriendsOfFriends:
            image = [UIImage imageNamed:@"scope_drag_inner_fof.png"];
            break;
        case STStampedAPIScopeEveryone:
            image = [UIImage imageNamed:@"scope_drag_inner_all.png"];
            break;
        default:
            break;
    }
    
    return image;
    
}


#pragma mark - Gestures

- (void)press:(UILongPressGestureRecognizer*)gesture {
    
    CGPoint position = [gesture locationInView:self];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
       
        _firstPress = YES;
        _beginPress = position;
        if (!_textCallout) {
            
            STStampedAPIScope scope = [self scopeForPosition:position];
            CGPoint viewPosition = [self positionForScope:scope];
            STTextCalloutView *view = [[STTextCalloutView alloc] init];
            [view setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
            [self.superview addSubview:view];
            viewPosition.y -= 20.0f;
            [view showFromPosition:[self convertPoint:viewPosition toView:self.superview] animated:YES];
            [view release];
            _textCallout = view;
            
        }
        
    }
    
    if (!_dragging && (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled)) {
        
        _firstPress = NO;
        if (_textCallout) {
            [_textCallout removeFromSuperview], _textCallout = nil;
        }
        
    }
    
}

- (void)pan:(UIPanGestureRecognizer*)gesture {
    [_timer invalidate];
    self.timer = nil;
    
    CGPoint position = [gesture locationInView:self];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        _dragging = YES;
        _prevScope = _scope;
        
        if (!_firstPress) {
            _firstPan = YES;
        }
                
        if (!_textCallout) {
            STTextCalloutView *view = [[STTextCalloutView alloc] init];
            [self.superview addSubview:view];
            _textCallout = view;
            [view release];
        }
        
    }
    
    STStampedAPIScope scope = [self scopeForPosition:position];
    if (_scope != scope) {
        _firstPan = NO;
    }
    
    if (_textCallout) {
        
        [_textCallout setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
        if (_prevScope != scope) {
            _draggingView.image = [self imageForScope:scope];
            _prevScope = scope;
        }

        if (!_firstPan && (gesture.state == UIGestureRecognizerStateBegan || gesture.state == UIGestureRecognizerStateChanged)) {
            
            __block UIImageView *view = _draggingView;
            __block CGPoint viewPosition = view.layer.position;
            viewPosition.y -= 20.0f;

            [UIView animateWithDuration:0.1f animations:^{
                [_textCallout showFromPosition:[self convertPoint:viewPosition toView:self.superview] animated:NO];
                viewPosition = view.layer.position;
                viewPosition.x = [self positionForScope:scope].x;
                view.layer.position = viewPosition;
            }];
            
        } else {
            
            CGFloat maxX = [self positionForScope:STStampedAPIScopeEveryone].x;
            CGFloat minX = [self positionForScope:STStampedAPIScopeYou].x;

            UIImageView *view = _draggingView;
            CGPoint viewPosition = view.layer.position;
            viewPosition.y -= 20.0f;
            [_textCallout showFromPosition:[self convertPoint:viewPosition toView:self.superview] animated:NO];
            viewPosition = view.layer.position;
            viewPosition.x = MIN(position.x, maxX);
            viewPosition.x = MAX(minX, viewPosition.x);
            view.layer.position = viewPosition;
            self.timer = [NSTimer timerWithTimeInterval:.3 target:self selector:@selector(snapToClosest:) userInfo:nil repeats:NO];
            [[NSRunLoop mainRunLoop] addTimer:self.timer forMode:NSDefaultRunLoopMode];
        }
        
    }
    
    if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        if (_scope != scope) {
            [self setScopeExplicit:scope];
        }
        
        _dragging = NO;
        if (_textCallout) {
            [_textCallout removeFromSuperview], _textCallout=nil;
        }
        
    }    
}

- (void)hideTextPopover {
    
    if (_textCallout) {
        [_textCallout removeFromSuperview], _textCallout=nil;
    }
    
}

- (void)tappedPoint:(CGPoint)position {
    
    STStampedAPIScope scope = [self scopeForPosition:position];
    if (_scope != scope) {
        
        STStampedAPIScope currentScope = _scope;
        [self setScopeExplicit:scope];
        
        UIView *view = _draggingView;
        NSInteger diff = currentScope - _scope;
        if (diff < 0) {
            diff *= -1;
        }
        
        float fDiff = ((float)diff)/10.0f;
        CGPoint fromPos = [self positionForScope:currentScope];
        
        if (!_textCallout) {
            STTextCalloutView *view = [[STTextCalloutView alloc] init];
            [self.superview addSubview:view];
            _textCallout = view;
            [view release];
        }
        
        [_textCallout setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
        CGPoint viewPosition = view.layer.position;
        viewPosition.y -= 20.0f;
        [_textCallout showFromPosition:[self convertPoint:viewPosition toView:self.superview] animated:NO];
        [self performSelector:@selector(hideTextPopover) withObject:nil afterDelay:1.5f];
        
        [CATransaction begin];
        [CATransaction setAnimationDuration:0.3f];
        
        CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position"];
        animation.fromValue = [NSValue valueWithCGPoint:fromPos];
        animation.duration = fDiff;
        animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
        [view.layer addAnimation:animation forKey:nil];
        
        if (_textCallout) {
            
            animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
            animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
            animation.duration = fDiff;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [_textCallout.layer addAnimation:animation forKey:nil];
            
        }
        
        [CATransaction commit];
        
    }
}

- (void)tap:(UITapGestureRecognizer*)gesture {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(hideTextPopover) object:nil];
    CGPoint position = [gesture locationInView:self];
    [self tappedPoint:position];
}

- (void)snapToClosest:(id)notImportant {
    NSLog(@"Snapped to closest");
    [self.timer invalidate];
    self.timer = nil;
    //CGPoint position = CGPointMake(CGRectGetMidX(_draggingView.frame), CGRectGetMidY(_draggingView.frame));
    
    //self tappedPoint:position];
    CGPoint position = [self positionForScope:_scope];
    [UIView animateWithDuration:.1 animations:^{
        CGRect frame = _draggingView.frame;
        frame.origin.x = position.x - frame.size.width / 2 ;
        _draggingView.frame = frame;
    }];
}

#pragma mark -  UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    return YES;
}

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    
    if ([gestureRecognizer isKindOfClass:[UILongPressGestureRecognizer class]]) {
        return YES;
    }
    
    if ([gestureRecognizer isKindOfClass:[UIPanGestureRecognizer class]]) {
        if ([otherGestureRecognizer isKindOfClass:[UIPanGestureRecognizer class]]) {
            return NO;
        }
        return (gestureRecognizer.view == self);
    }
    
    return NO;
    
}



@end
