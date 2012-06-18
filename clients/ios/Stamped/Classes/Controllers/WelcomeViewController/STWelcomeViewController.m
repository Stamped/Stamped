//
//  STWelcomeViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "STWelcomeViewController.h"
#import "LoginViewController.h"
#import "WelcomePopoverView.h"
#import "DDMenuController.h"

@interface STWelcomeViewController ()

@end

@implementation STWelcomeViewController
@synthesize delegate;


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
        
        UIButton *closeButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [closeButton addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        [closeButton setImage:[UIImage imageNamed:@"welcome_popover_close.png"] forState:UIControlStateNormal];
        
        CGRect frame = CGRectMake(-12.0f, -16.0f, 44.0f, 44.0f);
        frame = [_popoverView convertRect:frame toView:self.view];
        closeButton.frame = frame;
        [self.view addSubview:closeButton];
        
    }
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    _popoverView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - Sign In

- (void)showSignIn {
    
    [_popoverView showOptionsView];
    
}

- (void)close:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewControllerDismiss:)]) {
        [self.delegate stWelcomeViewControllerDismiss:self];
    }
    
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

- (void)popIn {
    
    CGFloat duration = 0.55f;
    CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
    scale.duration = duration;
    scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:.6f], [NSNumber numberWithFloat:1.15f], [NSNumber numberWithFloat:.85f], [NSNumber numberWithFloat:1.f], nil];
    
    CABasicAnimation *fadeIn = [CABasicAnimation animationWithKeyPath:@"opacity"];
    fadeIn.duration = duration * .4f;
    fadeIn.fromValue = [NSNumber numberWithFloat:0.f];
    fadeIn.toValue = [NSNumber numberWithFloat:1.f];
    fadeIn.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut];
    fadeIn.fillMode = kCAFillModeForwards;
    
    CAAnimationGroup *group = [CAAnimationGroup animation];
    [group setAnimations:[NSArray arrayWithObjects:scale, fadeIn, nil]];
    group.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    [_popoverView.layer addAnimation:group forKey:nil];
    
}


#pragma mark - WelcomePopoverViewDelegate

- (void)welcomePopoverViewSelectedTwitter:(WelcomePopoverView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewController:selectedOption:)]) {
        [self.delegate stWelcomeViewController:self selectedOption:STWelcomeViewControllerOptionTwitter];
    }
    
}

- (void)welcomePopoverViewSelectedFacebook:(WelcomePopoverView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewController:selectedOption:)]) {
        [self.delegate stWelcomeViewController:self selectedOption:STWelcomeViewControllerOptionFacebook];
    }

}

- (void)welcomePopoverViewSelectedEmail:(WelcomePopoverView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewController:selectedOption:)]) {
        [self.delegate stWelcomeViewController:self selectedOption:STWelcomeViewControllerOptionSignup];
    }

}

- (void)welcomePopoverViewSelectedLogin:(WelcomePopoverView*)view {

    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewController:selectedOption:)]) {
        [self.delegate stWelcomeViewController:self selectedOption:STWelcomeViewControllerOptionLogin];
    }
    
}

- (void)welcomePopoverViewSelectedClose:(WelcomePopoverView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stWelcomeViewControllerDismiss:)]) {
        [self.delegate stWelcomeViewControllerDismiss:self];
    }
    
}


@end
