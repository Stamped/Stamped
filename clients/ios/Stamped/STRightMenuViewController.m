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
      //_categories = [[NSArray alloc] initWithObjects:@"music", @"food", @"book", @"film", @"other", nil];
      _categories = [[NSArray alloc] initWithObjects:@"music", @"apps", @"books", @"movies", @"places", nil];
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
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]];
        [self.view addSubview:imageView];
        imageView.layer.doubleSided = NO;
        imageView.layer.transform = CATransform3DMakeScale(-1.0f, 1.0f, 1.0f);
        [imageView release];
        
        UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:self.view.bounds];
        scrollView.backgroundColor = [UIColor clearColor];
        scrollView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        scrollView.showsVerticalScrollIndicator = NO;
        scrollView.showsHorizontalScrollIndicator = NO;
        scrollView.alwaysBounceVertical = YES;
        scrollView.alwaysBounceHorizontal = NO;
        [self.view addSubview:scrollView];
        _scrollView = [scrollView retain];
        [scrollView release];
        
        CGRect frame = CGRectMake(self.scrollView.frame.size.width - 76.0f, 30.0f, 50.0f, 50.0f);
        
        // close
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        [button setImage:[UIImage imageNamed:@"create_menu_close.png"] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        button.frame = frame;
        [_scrollView addSubview:button];
        [_buttons addObject:button];
        
        for (NSInteger i = 0; i < self.categories.count; i++) {
            
            frame.origin.y += 60.0f;
            NSString *category = [self.categories objectAtIndex:i];
            UIImage *image = [UIImage imageNamed:[NSString stringWithFormat:@"create_menu_%@.png", category]];
            UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
            button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
            [button setImage:image forState:UIControlStateNormal];
            [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
            button.frame = frame;
            button.tag = i;
            [_scrollView addSubview:button];
            [_buttons addObject:button];

        }
        
        frame.origin.y += 60.0f;

        // more
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        [button setImage:[UIImage imageNamed:@"create_menu_more.png"] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(more:) forControlEvents:UIControlEventTouchUpInside];
        button.frame = frame;
        [_scrollView addSubview:button];
        [_buttons addObject:button];
        
        UIImageView *corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_right.png"]];
        [self.view addSubview:corner];
        [corner release];
        
        frame = corner.frame;
        frame.origin.x = (self.view.bounds.size.width - corner.frame.size.width);
        corner.frame = frame;

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
    
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.2f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut]];
    [CATransaction setCompletionBlock:^{
        //[view.layer setValue:[NSNumber numberWithFloat:1.0f] forKeyPath:@"transform.scale"];
    }];
    
    CAAnimationGroup *groupAnimation = [CAAnimationGroup animation];
    groupAnimation.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
    groupAnimation.removedOnCompletion = NO;
    groupAnimation.fillMode = kCAFillModeForwards;

    CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
    scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:1.0f], nil];
    
    //CABasicAnimation *scale = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
    //scale.fromValue = [NSNumber numberWithFloat:0.00000001f];
    //scale.toValue = [NSNumber numberWithFloat:1.0f];

    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.fromValue = [NSNumber numberWithFloat:0.0f];
    opacity.toValue = [NSNumber numberWithFloat:1.0f];
    
    [groupAnimation setAnimations:[NSArray arrayWithObjects:scale, nil]];
    [view.layer addAnimation:groupAnimation forKey:nil];

    [CATransaction commit];
    
}

- (void)animateIn {
    if (_hasAnimated) return;
    _hasAnimated = NO;
    
    float delay = 0.1f;
    for (UIView *view in _buttons) {

        CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
        scale.calculationMode = @"cubic";
        scale.duration = 0.15f;
        scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:1.0f], nil];
        scale.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
        [view.layer addAnimation:scale forKey:nil];
        
        delay += 0.04f;
    }
    
}


#pragma mark - Actions

- (void)close:(id)sender  {

    DDMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller showRootController:YES];
    
}

- (void)more:(id)sender {
    
    
}

- (void)buttonHit:(UIButton*)button {
   
    NSString *category = [self.categories objectAtIndex:button.tag];
    STEntitySearchController *controller = [[STEntitySearchController alloc] initWithCategory:category andQuery:nil];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [menuController pushViewController:controller animated:YES];
    [controller release];
    
}


@end
