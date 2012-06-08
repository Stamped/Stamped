//
//  LoginLoadingView.m
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import "LoginLoadingView.h"

@implementation LoginLoadingView

@synthesize titleLabel;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
        view.frame = CGRectMake((self.bounds.size.width-18.0f)/2, (self.bounds.size.height-18.0f)/2, 18.0f, 18.0f);
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        [self addSubview:view];
        [view release];
        _activityView = view;
        [_activityView startAnimating];
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-font.lineHeight, self.bounds.size.width, font.lineHeight)];
        label.backgroundColor = [UIColor clearColor];
        label.font = font;
        label.textAlignment = UITextAlignmentCenter;
        label.textColor = [UIColor colorWithWhite:0.749f alpha:1.0f];
        label.shadowColor = [UIColor colorWithWhite:1.0f alpha:0.6f];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:label];
        [label release];
        self.titleLabel = label;
        
    }
    return self;
    
}

- (void)dealloc {
    self.titleLabel = nil;
    [super dealloc];
}

@end