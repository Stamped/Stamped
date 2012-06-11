//
//  STButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STButton.h"
#import "Util.h"

@interface STButton ()

@property (nonatomic, readonly, retain) UIView* normalView;
@property (nonatomic, readonly, retain) UIView* activeView;
@property (nonatomic, readonly, assign) BOOL touched;
@property (nonatomic, readwrite, retain) NSObject* token;
@property (nonatomic, readwrite, assign) BOOL animating;

@end

@implementation STButton

@synthesize normalView = normalView_;
@synthesize activeView = activeView_;
@synthesize target = target_;
@synthesize action = action_;
@synthesize enabled = enabled_;
@synthesize touched = touched_;
@synthesize message = message_;
@synthesize token = _token;

- (id)initWithFrame:(CGRect)frame 
         normalView:(UIView*)normalView 
         activeView:(UIView*)activeView 
             target:(id)target 
          andAction:(SEL)selector
{
    self = [super initWithFrame:frame];
    if (self) {
        normalView_ = [normalView retain];
        activeView_ = [activeView retain];
        target_ = target;
        action_ = selector;
        enabled_ = YES;
        touched_ = NO;
        [self addSubview:normalView];
        [self addSubview:activeView];
        normalView.hidden = NO;
        normalView.alpha = 1;
        activeView.hidden = YES;
        activeView.alpha = 0;
    }
    return self;
}

- (void)dealloc
{
    [normalView_ release];
    [activeView_ release];
    [message_ release];
    [_token release];
    [super dealloc];
}

static CGFloat _duration = .25; 

- (void)setTouched:(BOOL)touched {
    if (touched != touched_) {
        touched_ = touched;
        self.normalView.hidden = NO;
        self.activeView.hidden = NO;
        if (touched_) {
            [UIView animateWithDuration:.05 animations:^{
                self.activeView.alpha = 1;
                self.normalView.alpha = 0;
            } completion:^(BOOL finished) {
            }];
        }
        else {
            [UIView animateWithDuration:_duration 
                                  delay:0
                                options:UIViewAnimationOptionBeginFromCurrentState
                             animations:^{
                                 self.normalView.alpha = 1;
                                 self.activeView.alpha = 0;
                             } 
                             completion:^(BOOL finished) {
                             }];
            [UIView animateWithDuration:_duration animations:^{
            } completion:^(BOOL finished) {
            }];
        }
        [self setNeedsDisplay];
    }
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
    //NSLog(@"touchesBegan");
    self.touched = YES;
    self.token = nil;
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {  
    //NSLog(@"touchesCancelled");
    self.touched = NO;
}

- (void)turnOff:(id)token {
    if ([token isEqual:self.token]) {
        self.token = nil;
        self.touched = NO;
    }
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
    //NSLog(@"touchesEnded");
    //TODO fix for cancellation
    self.token = [[[NSObject alloc] init] autorelease];
    [self performSelector:@selector(turnOff:) withObject:self.token afterDelay:.1];
    UITouch* touch = [touches anyObject];
    if (CGRectContainsPoint(CGRectMake(0, 0, self.frame.size.width, self.frame.size.height), [touch locationInView:self])) {
        id message = self.message;
        if (!message) {
            message = self;
        }
        [self.target performSelector:self.action withObject:message];
    }
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
    
}

+ (STButton*)buttonWithNormalImage:(UIImage*)normalImage
                       activeImage:(UIImage*)activeImage 
                            target:(id)target 
                         andAction:(SEL)selector {
    UIImageView* normalView = [[[UIImageView alloc] initWithImage:normalImage] autorelease];
    UIImageView* activeView = [[[UIImageView alloc] initWithImage:activeImage] autorelease];
    return [[[STButton alloc] initWithFrame:normalView.frame normalView:normalView activeView:activeView target:target andAction:selector] autorelease];
}

@end
