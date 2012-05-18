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
#import "AccountManager.h"
#import "STImageCache.h"

@interface STSliderScopeView (Internal)
- (UIImageView*)imageViewForScope:(STStampedAPIScope)scope;
- (void)setUserImageViewImage:(UIImage*)image;
@end

@implementation STSliderScopeView
@synthesize scope=_scope;
@synthesize longPress=_longPress;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
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
        
        UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"scope_track.png"]];
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
        
        imageView = [[UIImageView alloc] initWithFrame:_draggingView.bounds];
        imageView.contentMode = UIViewContentModeCenter;
        [_draggingView addSubview:imageView];
        _userImageView = imageView;
        _userImageView.hidden = YES;
        [imageView release];

        User *user = [AccountManager sharedManager].currentUser;
        if (user) {
            
            UIImage *image = [[STImageCache sharedInstance] cachedUserImageForUser:(id<STUser>)user size:STProfileImageSize46];
            if (image) {
                
                [self setUserImageViewImage:image];
                
            } else {
                
                [[STImageCache sharedInstance] userImageForUser:(id<STUser>)user size:STProfileImageSize46 andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                    [self setUserImageViewImage:image];
                }];
                
            }
        }
                
    }
    return self;
}

- (void)dealloc {
    _userImageView = nil;
    _textPopover = nil;
    [super dealloc];
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    _draggingView.layer.position = [self positionForIndex:_scope];
    
    
}

- (CGPoint)positionForIndex:(NSInteger)index {
    
    CGFloat width = (self.bounds.size.width-40.0f)/4;
    for (NSInteger i = 0; i < 4; i++) {
        UIView *view = [self viewWithTag:(i+1)*100];
        CGPoint position = view.layer.position;
        position.x = floorf((width*i) + (width/2) + 20.0f);
        position.y = floorf((self.bounds.size.height/2) + 2.0f);
        if (i == index) {
            return position;
        }
    }
    
    return CGPointZero;
    
}


#pragma mark - Helpers

- (void)pauseLayer:(CALayer*)layer {
    
    CFTimeInterval time = [layer convertTime:CACurrentMediaTime() toLayer:nil];
    layer.speed = 0.0;
    layer.timeOffset = time;
    
}

- (void)resumeLayer:(CALayer*)layer {
    
    CFTimeInterval time = layer.timeOffset;
    layer.speed = 1.0;
    layer.timeOffset = 0.0;
    layer.beginTime = 0.0;
    CFTimeInterval timeSince = [layer convertTime:CACurrentMediaTime() toLayer:nil] - time;
    layer.beginTime = timeSince;
    
}

- (void)hideTitleForView:(UIView*)view {
        
    __block UIView *label = [view viewWithTag:11];
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.6f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
    [CATransaction setCompletionBlock:^{
        if (label) {
            [label removeFromSuperview];
        }
    }];
    
    if (label) {
        CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
        opacity.fromValue = [NSNumber numberWithFloat:1.0f];
        opacity.toValue = [NSNumber numberWithFloat:0.0f];
        opacity.removedOnCompletion = NO;
        opacity.fillMode = kCAFillModeForwards;
        [label.layer addAnimation:opacity forKey:nil];
    }
    
    CABasicAnimation *transform = [CABasicAnimation animationWithKeyPath:@"transform.translation.y"];
    transform.fromValue = [NSNumber numberWithFloat:-4.0f];
    transform.toValue = [NSNumber numberWithFloat:0.0f];
    [view.layer addAnimation:transform forKey:nil];
    [view.layer setValue:[NSNumber numberWithFloat:0.0f] forKeyPath:@"transform.translation.y"];
    
    [CATransaction commit];
    
}

- (void)flashTitle:(NSString*)title forView:(UIView*)view animated:(BOOL)animated {
    
    if ([view viewWithTag:11]) {
        
        [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(hideTitleForView:) object:view];
        
        UILabel *label = (UILabel*)[view viewWithTag:11];
        label.text = title;
        [label sizeToFit];
        CGRect frame = label.frame;
        frame.origin.x = floorf((view.bounds.size.width-frame.size.width)/2);
        frame.origin.y = view.bounds.size.height - 6.0f;
        label.frame = frame;
        
        [self performSelector:@selector(hideTitleForView:) withObject:view afterDelay:2.0f];
        
        return;
        
    }
    
    [view.layer removeAllAnimations];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.tag = 11;
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor whiteColor];
    label.font = [UIFont boldSystemFontOfSize:8];
    label.shadowOffset = CGSizeMake(0.0f, -1.0f);
    label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.7f];
    label.text = title;
    label.layer.opacity = 0.0f;
    [view addSubview:label];
    [label sizeToFit];
    [label release];
    
    CGRect frame = label.frame;
    frame.origin.x = floorf((view.bounds.size.width-frame.size.width)/2);
    frame.origin.y = view.bounds.size.height - 6.0f;
    label.frame = frame;
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:animated ? 0.3f : 0.001f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
    [CATransaction setCompletionBlock:^{
        [view.layer setValue:[NSNumber numberWithFloat:-4.0f] forKeyPath:@"transform.translation.y"];
        [view.layer removeAllAnimations];
        [self performSelector:@selector(hideTitleForView:) withObject:view afterDelay:2.0f];
   }];
    
    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:0.0f];
    opacity.toValue = [NSNumber numberWithFloat:1.0f];
    //opacity.beginTime = [label.layer convertTime:CACurrentMediaTime() toLayer:nil] + 0.3f;
    opacity.removedOnCompletion = NO;
    opacity.fillMode = kCAFillModeForwards;
    [label.layer addAnimation:opacity forKey:nil];
    
    CABasicAnimation *transform = [CABasicAnimation animationWithKeyPath:@"transform.translation.y"];
    transform.fromValue = [NSNumber numberWithFloat:0.0f];
    transform.toValue = [NSNumber numberWithFloat:-4.0f];
    //transform.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + 0.3f;
    transform.removedOnCompletion = NO;
    transform.fillMode = kCAFillModeForwards;
    [view.layer addAnimation:transform forKey:nil];
    
    [CATransaction commit];
    
}

- (void)addTitle:(NSString*)title toView:(UIView*)view animated:(BOOL)animated {
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.tag = 11;
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor whiteColor];
    label.font = [UIFont boldSystemFontOfSize:8];
    label.shadowOffset = CGSizeMake(0.0f, -1.0f);
    label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.7f];
    label.text = title;
    label.layer.opacity = 0.0f;
    [view addSubview:label];
    [label sizeToFit];
    [label release];

    CGRect frame = label.frame;
    frame.origin.x = floorf((view.bounds.size.width-frame.size.width)/2);
    frame.origin.y = view.bounds.size.height - 4.0f;
    label.frame = frame;
    
    if (animated) {
        
        [CATransaction begin];
        [CATransaction setAnimationDuration:0.3f];
        [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
        
        CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
        opacity.fromValue = [NSNumber numberWithFloat:0.0f];
        opacity.toValue = [NSNumber numberWithFloat:1.0f];
        opacity.beginTime = [label.layer convertTime:CACurrentMediaTime() toLayer:nil] + 0.3f;
        opacity.removedOnCompletion = NO;
        opacity.fillMode = kCAFillModeForwards;
        [label.layer addAnimation:opacity forKey:nil];
        
        CABasicAnimation *transform = [CABasicAnimation animationWithKeyPath:@"transform.translation.y"];
        transform.fromValue = [NSNumber numberWithFloat:0.0f];
        transform.toValue = [NSNumber numberWithFloat:-4.0f];
        transform.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + 0.3f;
        transform.removedOnCompletion = NO;
        transform.fillMode = kCAFillModeForwards;
        [view.layer addAnimation:transform forKey:nil];
        
        [CATransaction commit];
        
    }
    
}

- (void)showAll {
    
    CGFloat width = (self.bounds.size.width-40.0f)/4;
    for (NSInteger i = 0; i < 4; i++) {
       
        if (i != _scope) {
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[self imageForScope:i]];
            [self addSubview:imageView];
            [self addTitle:[self titleForScope:i] toView:imageView animated:YES];
            [imageView release];
            imageView.tag = (i+1)*100;
            
            CGPoint position = imageView.layer.position;
            position.x = floorf((width*i) + (width/2) + 20.0f);
            position.y = (self.bounds.size.height/2);
            imageView.layer.position = position;
            
            [imageView.layer addAnimation:[self inAnimation] forKey:nil];
            imageView.layer.opacity = 1.0f;
        }

    }
    
}

- (void)hideAll {
        
    [CATransaction begin];
    [CATransaction setCompletionBlock:^{
        for (NSInteger i = 0; i < 4; i++) {
            UIView *view = [self viewWithTag:(i+1)*100];
            if (view) {
                [view removeFromSuperview];
            }
        }
    }];
    for (NSInteger i = 0; i < 4; i++) {
        UIView *view = [self viewWithTag:(i+1)*100];
        if (view) {
            
            UIView *label = [view viewWithTag:11];
            if (label) {
                [label removeFromSuperview];
            }
            
            [view.layer addAnimation:[self outAnimation] forKey:nil];
            view.layer.opacity = 0.0f;
        }
    }
    [CATransaction commit];
    
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope animated:(BOOL)animated {
    _scope = scope;
    
    if (!_dragging) {
        _draggingView.layer.position = [self positionForIndex:_scope];
        _draggingView.image = [self imageForScope:_scope];
        _userImageView.hidden = (_scope != STStampedAPIScopeYou);
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
    
    if (_userImageView && image) {
        UIGraphicsBeginImageContextWithOptions(CGSizeMake(24, 28), NO, 0);
        CGContextRef ctx = UIGraphicsGetCurrentContext();
        CGRect rect = CGContextGetClipBoundingBox(ctx);
        rect.size.height -= 4.0f;
        CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:12.0f].CGPath);
        CGContextClip(ctx);
        
        [image drawInRect:rect];
        _userImageView.image = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
    }
    
}


#pragma mark - Getters (Internal)

- (UIView*)viewForScope:(STStampedAPIScope)scope {
    
    return [self viewWithTag:(scope+1)*100];
    
}
    
- (NSString*)titleForScope:(STStampedAPIScope)scope {
    
    NSString *string = nil;
    switch (scope) {
        case STStampedAPIScopeYou:
            string = NSLocalizedString(@"you", @"you");
            break;
        case STStampedAPIScopeFriends:
            string = NSLocalizedString(@"you + friends", @"you + friends");
            break;
        case STStampedAPIScopeFriendsOfFriends:
            string = NSLocalizedString(@"friends of friends", @"friends of friends");
            break;
        case STStampedAPIScopeEveryone:
            string = NSLocalizedString(@"everyone", @"everyone");
            break;
        default:
            break;
    }
    
    return string;
    
}

- (STStampedAPIScope)scopeForPosition:(CGPoint)position {
    
    CGFloat width = (self.bounds.size.width-40.0f)/4;
    CGRect rect = CGRectMake(20.0f, 0.0f, width, self.bounds.size.height);
    for (NSInteger i = 0; i < 4; i++) {
        if (CGRectContainsPoint(rect, position)) {
            return i;
        }
        rect.origin.x += width;
    }
    
    if (position.x <= 20.0f) {
        return STStampedAPIScopeYou;
    }

    return STStampedAPIScopeEveryone; // defaults to you

}

- (UIImage*)imageForScope:(STStampedAPIScope)scope  {
    
    UIImage *image = nil;
    switch (scope) {
        case STStampedAPIScopeYou:
            image = [UIImage imageNamed:@"scope_drag_inner_you.png"];
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


#pragma mark - Animations

- (CAKeyframeAnimation*)popAnimation {
    
    CAKeyframeAnimation *animation = [CAKeyframeAnimation animation];
    animation.duration = 0.3f;
    animation.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.9f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:1.0f], nil];
    return animation;
    
}

- (CAAnimationGroup*)inAnimation {
    
    CAAnimationGroup *animation = [CAAnimationGroup animation];
    animation.duration = 0.2f;
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    
    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:0.0f];
    opacity.toValue = [NSNumber numberWithFloat:1.0f];
    
    CABasicAnimation *scale = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
    scale.fromValue = [NSNumber numberWithFloat:0.0f];
    scale.toValue = [NSNumber numberWithFloat:1.0f];
    
    [animation setAnimations:[NSArray arrayWithObjects:opacity, scale, nil]];
    
     return animation;
    
}

- (CAAnimationGroup*)outAnimation {
    
    CAAnimationGroup *animation = [CAAnimationGroup animation];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    animation.duration = 0.2f;
    
    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:1.0f];
    opacity.toValue = [NSNumber numberWithFloat:0.0f];
    
    CABasicAnimation *scale = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
    scale.fromValue = [NSNumber numberWithFloat:1.0f];
    scale.toValue = [NSNumber numberWithFloat:0.0f];
    
    [animation setAnimations:[NSArray arrayWithObjects:scale, opacity, nil]];
    
    return animation;
}


#pragma mark - Gestures

- (void)press:(UILongPressGestureRecognizer*)gesture {
    
    CGPoint position = [gesture locationInView:self];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        _firstPress = YES;
        _beginPress = position;
        if (!_textPopover) {
            STTextPopoverView *view = [[STTextPopoverView alloc] initWithFrame:CGRectZero];
            _textPopover = [view retain];
            [_textPopover showFromView:self position:position animated:YES];
        }
        
        //[self showAll];
        
    }
    
    if (_textPopover) {
        STStampedAPIScope scope = [self scopeForPosition:position];
        _textPopover.title = [self titleForScope:scope];            
        CGPoint viewPosition = [self positionForIndex:scope];
        viewPosition.y -= 46.0f;
        [_textPopover showFromView:self position:viewPosition animated:NO];
    }
    
    if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        _firstPress = NO;
       // [self hideAll];
        
        if (_textPopover) {
            [_textPopover removeFromSuperview];
            [_textPopover release];
            _textPopover = nil;
        }
        
    }
    
}

- (void)pan:(UIPanGestureRecognizer*)gesture {
    
    CGPoint position = [gesture locationInView:self];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        _dragging = YES;
        _prevScope = _scope;
        
        if (!_firstPress) {
            _firstPan = YES;
        }
        
        [self hideAll];
        
        if (!_textPopover) {
            STTextPopoverView *view = [[STTextPopoverView alloc] initWithFrame:CGRectZero];
            _textPopover = [view retain];
        }
        
    }
    
    STStampedAPIScope scope = [self scopeForPosition:position];
    if (_scope != scope) {
        _firstPan = NO;
    }
    
    if (_textPopover) {
        
        _textPopover.title = [self titleForScope:scope];
        if (_prevScope != scope) {
            _draggingView.image = [self imageForScope:scope];
            _userImageView.hidden = (scope != STStampedAPIScopeYou);
            _prevScope = scope;
        }

        if (!_firstPan) {
            
            __block UIImageView *view = _draggingView;
            __block CGPoint viewPosition = view.layer.position;
            viewPosition.y -= 46.0f;

            [UIView animateWithDuration:0.1f animations:^{
                [_textPopover showFromView:self position:viewPosition animated:NO];
                viewPosition = view.layer.position;
                viewPosition.x = [self positionForIndex:scope].x;
                view.layer.position = viewPosition;
            }];
            
        } else {
            
            UIImageView *view = _draggingView;
            CGPoint viewPosition = view.layer.position;
            viewPosition.y -= 46.0f;
            [_textPopover showFromView:self position:viewPosition animated:NO];
            viewPosition = view.layer.position;
            viewPosition.x = position.x;
            view.layer.position = viewPosition;
            
        }
        
    }
    
    if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        if (_scope != scope) {
            [self setScopeExplicit:scope];
        }
        
        _dragging = NO;
        if (_textPopover) {
            [_textPopover hide];
            [_textPopover release];
            _textPopover = nil;
        }
        
    }    
}

- (void)hideTextPopover {
    
    if (_textPopover) {
        [_textPopover hide];
        [_textPopover release];
        _textPopover = nil;
    }
    
}

- (void)tap:(UITapGestureRecognizer*)gesture {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(hideTextPopover) object:nil];
    CGPoint position = [gesture locationInView:self];
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
        CGPoint fromPos = [self positionForIndex:currentScope];
        
        if (!_textPopover) {
            STTextPopoverView *view = [[STTextPopoverView alloc] initWithFrame:CGRectZero];
            _textPopover = [view retain];
        }
        
        _textPopover.title = [self titleForScope:scope];
        CGPoint viewPosition = view.layer.position;
        viewPosition.y -= 46.0f;
        [_textPopover showFromView:self position:viewPosition animated:NO];
        [self performSelector:@selector(hideTextPopover) withObject:nil afterDelay:1.5f];
        
        [CATransaction begin];
        [CATransaction setAnimationDuration:0.3f];
        
        CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position"];
        animation.fromValue = [NSValue valueWithCGPoint:fromPos];
        animation.duration = fDiff;
        animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
        [view.layer addAnimation:animation forKey:nil];
        
        if (_textPopover) {
            
            animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
            animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
            animation.duration = fDiff;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [_textPopover.layer addAnimation:animation forKey:nil];
            
        }
        
        [CATransaction commit];
        
    }

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
        return NO;
    }
    
    return YES;
    
}



@end
