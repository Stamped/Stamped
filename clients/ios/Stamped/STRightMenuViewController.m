//
//  STRightMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRightMenuViewController.h"
#import "STEntitySearchController.h"
#import "DDMenuController.h"

@interface STRightMenuViewController ()
@property (nonatomic,readonly,retain) NSArray *categories;
@property(nonatomic,strong) UIScrollView *scrollView;
@end

@implementation STRightMenuViewController

@synthesize categories = _categories;
@synthesize scrollView = _scrollView;

- (id)init {
  if ((self = [super init])) {
      _categories = [[NSArray alloc] initWithObjects:@"music", @"food", @"book", @"film", @"other", nil];
      _buttons = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc {
    [_categories release], _categories=nil;
    self.scrollView = nil;
    [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
    
    if (!_scrollView) {
        
        UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:self.view.bounds];
        scrollView.backgroundColor = [UIColor darkGrayColor];
        scrollView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        scrollView.showsVerticalScrollIndicator = NO;
        scrollView.showsHorizontalScrollIndicator = NO;
        scrollView.alwaysBounceVertical = YES;
        scrollView.alwaysBounceHorizontal = NO;
        [self.view addSubview:scrollView];
        _scrollView = [scrollView retain];
        [scrollView release];
        
        CGRect frame = CGRectMake(self.scrollView.frame.size.width - 86.0f, 20.0f, 70.0f, 70.0f);
        
        for (NSInteger i = 0; i < self.categories.count; i++) {
            
            NSString *category = [self.categories objectAtIndex:i];

            //UIImage *image = nil; // need images
            //UIImage *imageHi = nil; // need images
            
            UIButton *button = [UIButton buttonWithType:UIButtonTypeRoundedRect];
            [button setTitle:category forState:UIControlStateNormal];
            button.titleLabel.font = [UIFont systemFontOfSize:10];
            
            button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
            // [button setImage:image forState:UIControlStateNormal];
            //  [button setImage:image forState:UIControlStateHighlighted];
            [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
            button.frame = frame;
            button.tag = i;
            [_scrollView addSubview:button];
            [_buttons addObject:button];
            frame.origin.y += 80.0f;

        }

        
    }

    

}

- (void)viewDidUnload {
    [super viewDidUnload];
    [_buttons removeAllObjects];
    self.scrollView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self animateIn];
}


#pragma mark - Animations

- (void)popInView:(UIView*)view withDelay:(CGFloat)delay {
    
    [view.layer setValue:[NSNumber numberWithFloat:0.0f] forKeyPath:@"opacity"];
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.1f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut]];
    [CATransaction setCompletionBlock:^{
        [view.layer setValue:[NSNumber numberWithFloat:1.0f] forKeyPath:@"opacity"];
    }];
    
    CAAnimationGroup *groupAnimation = [CAAnimationGroup animation];
    groupAnimation.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
    groupAnimation.removedOnCompletion = NO;
    groupAnimation.fillMode = kCAFillModeForwards;

    //CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
    //scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.01f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:1.0f], nil];
    
    CABasicAnimation *scale = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
    scale.fromValue = [NSNumber numberWithFloat:0.0f];
    scale.toValue = [NSNumber numberWithFloat:1.0f];

    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:0.0f];
    opacity.toValue = [NSNumber numberWithFloat:1.0f];
    
    [groupAnimation setAnimations:[NSArray arrayWithObjects:scale, opacity, nil]];
    [view.layer addAnimation:groupAnimation forKey:nil];

    [CATransaction commit];
    
}

- (void)animateIn {
    if (_hasAnimated) return;
    _hasAnimated = NO;
    
    float delay = 0.1f;
    for (UIView *view in _buttons) {
        [self popInView:view withDelay:delay];
        delay += 0.04f;
    }
    
}


#pragma mark - Actions

- (void)buttonHit:(UIButton*)button {
   
    NSString *category = [self.categories objectAtIndex:button.tag];
    STEntitySearchController *controller = [[STEntitySearchController alloc] initWithCategory:category andQuery:nil];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [menuController setRootController:controller animated:YES];
    [controller release];
    
}


@end
