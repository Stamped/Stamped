//
//  STStampSwitch.m
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import "STStampSwitch.h"

@implementation STStampSwitch
@synthesize on=_on;

- (id)initWithFrame:(CGRect)frame {
    frame.size.width = 64.0f;
    frame.size.height = 30.0f;
    if ((self = [super initWithFrame:frame])) {
        
        UIImage *image = [UIImage imageNamed:@"switch_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        CGRect frame = imageView.frame;
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        [self addSubview:imageView];
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"switch_stamp_icon.png"]];
        [self addSubview:imageView];
        imageView.layer.position = CGPointMake(16, (self.bounds.size.height/2));
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"switch_check_icon.png"]];
        [self addSubview:imageView];
        imageView.layer.position = CGPointMake((self.bounds.size.width-((16+imageView.bounds.size.width)/2)), (self.bounds.size.height/2));
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"switch_btn.png"]];
        [self addSubview:imageView];
        _handle = imageView;
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"switch_stamp_icon_hi.png"]];
        [_handle addSubview:imageView];
        imageView.layer.position = CGPointMake((_handle.bounds.size.width/2), (_handle.bounds.size.height/2));
        _handleIcon = imageView;
        [imageView release];
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        [self addGestureRecognizer:gesture];
        [gesture release];
        
        UIPanGestureRecognizer *pan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(pan:)];
        [self addGestureRecognizer: pan];
        [pan release];
        
    }
    return self;
}


#pragma mark - Setters

- (void)setOn:(BOOL)on animated:(BOOL)animated {
    _on = on;
    
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    
    [UIView animateWithDuration:0.25f animations:^{
        
        _handleIcon.image = [UIImage imageNamed:_on ? @"switch_check_icon_hi.png" : @"switch_stamp_icon_hi.png"];
        
        CGRect frame = _handle.frame;
        frame.origin.x = _on ? ceilf(self.bounds.size.width - (frame.size.width-1.0f)) : 0.0f;
        _handle.frame = frame;
        
    } completion:^(BOOL finished) {
        
        NSArray *targets = [[self allTargets] allObjects];

        for (id target in targets) {
            
            NSArray *actions = [self actionsForTarget:target forControlEvent:[self allControlEvents]];
            for (id action in actions) {
                SEL selector = NSSelectorFromString(action);
                if ([target respondsToSelector:selector]) {
                    [target performSelector:selector withObject:self];
                }
            }
        }
        
    }];
    
    [UIView setAnimationsEnabled:_enabled];
    
}

- (void)setOn:(BOOL)on {
    [self setOn:on animated:NO];
}


#pragma mark - Gestures

- (void)pan:(UIPanGestureRecognizer*)gesture {
    
    CGPoint pos = [gesture locationInView:self];
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        _panDiff = (_handle.layer.position.x - pos.x);
    }
    
    CGPoint position = _handle.layer.position;
    position.x = MAX(floorf(_handle.bounds.size.width/2), (pos.x + _panDiff));
    position.x = MIN(ceilf(self.bounds.size.width - ((_handle.bounds.size.width-1.0f)/2)), position.x);
    _handle.layer.position = position;

    BOOL on = (_handle.layer.position.x > self.bounds.size.width / 2);
    if (on != _on) {
        _on = on;
        _handleIcon.image = [UIImage imageNamed:_on ? @"switch_check_icon_hi.png" : @"switch_stamp_icon_hi.png"];
    }
    
    if (gesture.state == UIGestureRecognizerStateCancelled || gesture.state == UIGestureRecognizerStateEnded) {
        
        _panDiff = 0.0f;
        [self setOn:on animated:YES];
        
    }
    
}

- (void)tapped:(UITapGestureRecognizer*)gesture {
    [self setOn:!_on animated:YES];
}


@end
