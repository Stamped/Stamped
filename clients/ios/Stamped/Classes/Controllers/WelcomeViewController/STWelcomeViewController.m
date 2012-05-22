//
//  STWelcomeViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "STWelcomeViewController.h"
#import "WelcomePopoverView.h"

@interface STWelcomeViewController ()

@end

@implementation STWelcomeViewController

- (id)init {
    if ((self = [super init])) {
        
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.6f];
    
    if (!_popoverView) {
        
        UIImage *image = [UIImage imageNamed:@"welcome_popover_bg.png"];
        
        WelcomePopoverView *view = [[WelcomePopoverView alloc] initWithFrame:CGRectMake((self.view.bounds.size.width-image.size.width)/2, 65.0f, image.size.width, self.view.bounds.size.height-132.0f)];
        view.delegate = (id<WelcomePopoverViewDelegate>)self;
        view.image = [image stretchableImageWithLeftCapWidth:0 topCapHeight:image.size.height/2];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self.view addSubview:view];
        _popoverView = view;
        [view release];
        
    }
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    _popoverView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - Animations

- (void)animateIn {
    
    __block UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"Default.png"]];
    imageView.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
    [self.view addSubview:imageView];
    [imageView release];
    
    CGRect frame = imageView.frame;
    frame.origin.y = -20.0f;
    imageView.frame = frame;
    
    imageView.layer.shadowOpacity = 0.7f;
    imageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    imageView.layer.shadowRadius = 10;
    imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;

    [CATransaction begin];
    [CATransaction setAnimationDuration:0.5f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut]];
    [CATransaction setCompletionBlock:^{
        [imageView removeFromSuperview];
    }];
    
    CGPoint toPos = CGPointMake(imageView.layer.position.x, -(imageView.bounds.size.height/2));
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position"];
    animation.fromValue = [NSValue valueWithCGPoint:imageView.layer.position];
    animation.toValue = [NSValue valueWithCGPoint:toPos];
    [imageView.layer addAnimation:animation forKey:nil];
    imageView.layer.position = toPos;
    
    [CATransaction commit];
    
}


#pragma mark - WelcomePopoverViewDelegate

- (void)welcomePopoverViewSelectedClose:(WelcomePopoverView*)view {
    
    [self.view removeFromSuperview];
    
}


@end
