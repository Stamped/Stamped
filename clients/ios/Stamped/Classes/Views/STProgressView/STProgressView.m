//
//  STProgressView.m
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import "STProgressView.h"

@implementation STProgressView
@synthesize progress=_progress;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        CALayer *layer = [CALayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.backgroundColor = [UIColor colorWithWhite:0.7f alpha:0.7f].CGColor;
        [self.layer addSublayer:layer];
        _progressLayer = layer;
        
        self.backgroundColor = [UIColor clearColor];
        self.layer.borderWidth = 2.0f;
        self.layer.borderColor = [UIColor colorWithWhite:0.7f alpha:0.7f].CGColor;
        
        _progress = 0.0f;
        self.layer.cornerRadius = self.bounds.size.height/2;
        
        CGRect frame = CGRectInset(self.bounds, 2, 2);
        frame.size.width = MIN(frame.size.width, frame.size.width * _progress);
        _progressLayer.frame = frame;
        _progressLayer.cornerRadius = _progressLayer.bounds.size.height/2;
        
        
    }
    return self;
}

- (void)setProgress:(CGFloat)progress animated:(BOOL)animated {
    progress = MAX(progress, 0.0f);
    progress = MIN(progress, 1.0f);
    _progress = progress;
    
    CGRect frame = CGRectInset(self.bounds, 2, 2);
    frame.size.width = MIN(frame.size.width, frame.size.width * _progress);
    
    if (animated) {
        [UIView beginAnimations:nil context:NULL];
        _progressLayer.frame = frame;
        [UIView commitAnimations];
    } else {
        _progressLayer.frame = frame;
    }    
    
}

- (void)setProgress:(CGFloat)progress {
    [self setProgress:progress animated:NO];
}

@end