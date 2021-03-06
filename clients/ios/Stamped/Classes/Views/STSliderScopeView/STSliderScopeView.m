//
//  STSliderScopeView.m
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//  Edited by Landon Judkins 7/22/12
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

@interface STSliderScopeView ()

- (void)setUserImageViewImage:(UIImage*)image;

@property (nonatomic, readonly, retain) STTextCalloutView* textCallout;
@property (nonatomic, readwrite, assign) BOOL dragging;
@property (nonatomic, readwrite, assign) NSTimeInterval dragBeginTime;
@property (nonatomic, readonly, retain) UIImageView* draggingView;
@property (nonatomic, readwrite, assign) CGPoint beginPress;
@property (nonatomic, readwrite, assign) BOOL firstPan;
@property (nonatomic, readwrite, assign) BOOL firstPress;
@property (nonatomic, readwrite, retain) UIImage* userImage;
@property (nonatomic, readwrite, assign) STStampedAPIScope prevScope;
@property (nonatomic, readwrite, assign) STSliderScopeStyle style; // default STSliderScopeStyleThree
@property (nonatomic, readwrite, retain) NSTimer* timer;

@end

@implementation STSliderScopeView

@synthesize textCallout = _textCallout;
@synthesize dragging = _dragging;
@synthesize dragBeginTime = _dragBeginTime;
@synthesize draggingView = _draggingView;
@synthesize beginPress = _beginPress;
@synthesize firstPan = _firstPan;
@synthesize firstPress = _firstPress;
@synthesize userImage = _userImage;
@synthesize prevScope = _prevScope;
@synthesize style = _style;

@synthesize scope=_scope;
@synthesize delegate;
@synthesize dataSource;
@synthesize selectedIndex=_selectedIndex;
@synthesize timer = _timer;

- (void)commonInit {
    
    STBlockUIView *background = [[[STBlockUIView alloc] initWithFrame:self.bounds] autorelease];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [self addSubview:background];
    [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
        
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
    
    UITapGestureRecognizer *tap = [[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tap:)] autorelease];
    tap.delegate = (id<UIGestureRecognizerDelegate>)self;
    [self addGestureRecognizer:tap];
    
    UIPanGestureRecognizer *pan = [[[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(pan:)] autorelease];
    pan.delegate = (id<UIGestureRecognizerDelegate>)self;
    [self addGestureRecognizer:pan];
    
    UIImageView *view = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:(_style == STSliderScopeStyleTwo) ? @"slider_track_2.png" : @"slider_track_3.png"]] autorelease];
    view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
    [self addSubview:view];
    CGRect frame = view.frame;
    frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
    frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
    view.frame = frame;
    
    _draggingView = [[UIImageView alloc] initWithImage:[self imageForScope:0]];
    [self addSubview:_draggingView];
    
    self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
    self.layer.shadowOpacity = 1;
    self.layer.shadowOffset = CGSizeMake(0, -1);
    
    _scope=-1;
    [self userUpdated:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(userUpdated:) name:STStampedAPIUserUpdatedNotification object:nil];
    
    
    _textCallout = [[STTextCalloutView alloc] init];
    _textCallout.hidden = YES;
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
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_userImage release];
    [self invalidateTimer];
    [_textCallout release];
    [_draggingView release];
    [super dealloc];
}

- (void)invalidateTimer {
    [self.timer invalidate];
    self.timer = nil;
}

- (void)triggerTimer {
    [self invalidateTimer];    
    self.timer = [NSTimer scheduledTimerWithTimeInterval:1.5f target:self selector:@selector(triggerFade:) userInfo:nil repeats:NO];
}

- (void)triggerFade:(id)notImportant {
    [self invalidateTimer];
    [self.textCallout hide:YES];
}

- (void)didMoveToSuperview {
    [self invalidateTimer];
    [self.textCallout removeFromSuperview];
    [self.superview addSubview:self.textCallout];
}

- (void)userUpdated:(id)notImportant {
    id<STUser> user = STStampedAPI.sharedInstance.currentUser;
    if (user) {
        UIImage *image = [STStampedAPI sharedInstance].currentUserImage;
        if (!image) {
            [[STImageCache sharedInstance] cachedUserImageForUser:user size:STProfileImageSize24];
        }
        if (image) {
            
            [self setUserImageViewImage:image];
            
        } else {
            
            [[STImageCache sharedInstance] userImageForUser:(id<STUser>)user size:STProfileImageSize24 andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                [self setUserImageViewImage:image];
            }];
            
        }
    }
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    self.draggingView.layer.position = [self positionForScope:_scope];
    
    
}

- (CGPoint)positionForScope:(STStampedAPIScope)scope {
    
    CGPoint pos = CGPointMake(floorf(self.bounds.size.width/2), floorf(self.bounds.size.height/2) + 1.0f);
    
    switch (scope) {
        case STStampedAPIScopeYou:
            pos.x = ((self.bounds.size.width/2) - ((_style == STSliderScopeStyleTwo) ? kSliderTwoTrackGap : kSliderTrackGap));
            break;
        case STStampedAPIScopeFriends:
            pos.x = _style == STSliderScopeStyleTwo ? ((self.bounds.size.width/2) + kSliderTwoTrackGap) : (self.bounds.size.width/2);;
            break;
        case STStampedAPIScopeEveryone:
            pos.x = ((self.bounds.size.width/2) + kSliderTrackGap);
            break;
        default:
            break;
    }
    
    return pos;
    
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope animated:(BOOL)animated {
    if (_scope == scope) return;
    _scope = scope;
    if (!self.dragging) {
        if (animated) {
            [self.textCallout setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];   
            self.textCallout.hidden = NO;
            self.draggingView.image = [self imageForScope:_scope];
            [self moveToScope:scope animated:YES duration:0.4 completion:^{
                if (self.delegate) {
                    [self setScopeExplicit:scope];
                }
                [self triggerTimer];
            }];
        }
        else {
            self.draggingView.layer.position = [self positionForScope:_scope];
            self.draggingView.image = [self imageForScope:_scope];
        }
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
        
        self.userImage = [UIGraphicsGetImageFromCurrentImageContext() retain];        
        UIGraphicsEndImageContext();
        
        if (self.scope == STStampedAPIScopeYou) {
            self.draggingView.image = self.userImage;
        }
        
    }
    
}


#pragma mark - Getters (Internal)

- (UIView*)viewForScope:(STStampedAPIScope)scope {
    
    return [self viewWithTag:(scope+1)*100];
    
}

- (NSString*)titleForScope:(STStampedAPIScope)scope {
    
    if ([(id)self.dataSource respondsToSelector:@selector(sliderScopeView:titleForScope:)]) {
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
            NSAssert1(NO, @"scope should not be %d", scope);
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
    
    if (self.style == STSliderScopeStyleTwo) {
        
        if (position.x < (self.frame.size.width/2)) {
            return STStampedAPIScopeYou;
        }
        else {
            return STStampedAPIScopeFriends;
        }
        
    }
    else {
        
        CGFloat xOrigin = (self.frame.size.width-60.0f)/2;
        CGRect rect = CGRectMake(xOrigin, 0.0f, 60.0f, self.frame.size.height);
        if (CGRectContainsPoint(rect, position)) {
            return STStampedAPIScopeFriends;
        } 
        else if (position.x < xOrigin) {
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
            image = [UIImage imageNamed:@"tastemakers_star"];
            break;
        default:
            break;
    }
    
    return image;
    
}

#pragma mark - Panning Animations

- (void)moveToScope:(STStampedAPIScope)scope animated:(BOOL)animated duration:(CGFloat)duration completion:(void (^)(void))completion {
    
    
    CGPoint fromPos = self.draggingView.layer.position;
    CGPoint toPos = [self positionForScope:scope];
    if (CGPointEqualToPoint(fromPos, toPos)) return;
    
    self.draggingView.layer.position = toPos;
    
    if (self.textCallout) {
        CGPoint pos = self.draggingView.layer.position;
        pos.y -= 20.0f;
        self.textCallout.hidden = NO;
        [self.textCallout showFromPosition:[self convertPoint:pos toView:self.superview] animated:NO];
    }
    
    BOOL disabled = [CATransaction disableActions];
    [CATransaction setDisableActions:!animated];
    
    [CATransaction begin];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
    [CATransaction setAnimationDuration:duration];
    [CATransaction setCompletionBlock:^{
        completion();        
    }];
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
    animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
    [self.draggingView.layer addAnimation:animation forKey:nil];
    
    if (self.textCallout) {
        
        fromPos = [self convertPoint:fromPos toView:self.superview];
        animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
        animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
        [self.textCallout.layer addAnimation:animation forKey:nil];
        
    }
    
    [CATransaction commit];
    [CATransaction setDisableActions:disabled];
    
}


#pragma mark - Gestures

- (void)pan:(UIPanGestureRecognizer*)gesture {
    [_timer invalidate];
    self.timer = nil;
    
    CGPoint position = [gesture locationInView:self];
    STStampedAPIScope scope = [self scopeForPosition:position];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        _dragging = YES;
        _prevScope = _scope;
        
        if (!_firstPress) {
            _firstPan = YES;
        }
        [[self textCallout] setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
        
    } else {
        
        if (_scope != scope) {
            _firstPan = NO;
        }
        
    }
    
    if (_prevScope != scope) {
        _draggingView.image = [self imageForScope:scope];
        [[self textCallout] setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
        _prevScope = scope;
    }
    
    if ((gesture.state == UIGestureRecognizerStateBegan || gesture.state == UIGestureRecognizerStateChanged)) {
        
        if (!_firstPan) {
            
            [self moveToScope:scope animated:YES duration:.1 completion:^{}];
        } else {
            
            CGFloat maxX = [self positionForScope:STStampedAPIScopeEveryone].x;
            CGFloat minX = [self positionForScope:STStampedAPIScopeYou].x;
            
            UIImageView *view = self.draggingView;
            CGPoint viewPosition = view.layer.position;
            viewPosition = view.layer.position;
            viewPosition.x = MIN(position.x, maxX);
            viewPosition.x = MAX(minX, viewPosition.x);
            view.layer.position = viewPosition;
            viewPosition.y -= 20.0f;
            [self triggerTimer];
            [self.textCallout showFromPosition:[self convertPoint:viewPosition toView:self.superview] animated:NO];
        }
        
    } else if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        CGPoint fromPos = _draggingView.layer.position;
        CGPoint toPos = [self positionForScope:scope];
        
        if (!CGPointEqualToPoint(fromPos, toPos)) {
            
            _draggingView.layer.position = toPos;
            
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            animation.duration = 0.1f;
            animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
            [_draggingView.layer addAnimation:animation forKey:nil];
            
            if (_textCallout) {
                CGPoint pos = _textCallout.layer.position;
                fromPos = [self convertPoint:fromPos toView:self.superview];
                toPos = [self convertPoint:toPos toView:self.superview];
                pos.x = toPos.x;
                _textCallout.layer.position = pos;
                animation = [CABasicAnimation animationWithKeyPath:@"position.x"];
                animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
                animation.duration = 0.1f;
                animation.fromValue = [NSNumber numberWithFloat:fromPos.x];
                [_textCallout.layer addAnimation:animation forKey:nil];
            }
            
        }
        
        if (_scope != scope) {
            [self setScopeExplicit:scope];
        }      
        
        _dragging = NO;
        [self triggerTimer];
        
    }    
}

- (void)tap:(UITapGestureRecognizer*)gesture {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(hideTextCallout) object:nil];
    STStampedAPIScope scope = [self scopeForPosition:[gesture locationInView:self]];
    
    BOOL differnt = _scope != scope;
    NSInteger diff = _scope - scope;
    if (diff < 0) {
        diff *= -1;
    }        
    float fDiff = ((float)diff)/10.0f;
    
    CGPoint pos = [_draggingView.layer position];
    pos.y -= 20.0f;
    [[self textCallout] setTitle:[self titleForScope:scope] boldText:[self boldTitleForScope:scope]];
    self.textCallout.hidden = NO;
    [self moveToScope:scope animated:YES duration:fDiff completion:^{
        if (differnt) {
            [self setScopeExplicit:scope];
        }
    }];
    [self triggerTimer];        
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
