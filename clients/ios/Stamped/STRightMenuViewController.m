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
- (void)animateIn:(BOOL)animated;
@property (nonatomic,readonly,retain) NSArray *categories;
@property(nonatomic,retain) UIScrollView *scrollView;
@property(nonatomic,retain) NSDictionary *categoryMapping; 
@end

@implementation STRightMenuViewController

@synthesize categories = _categories;
@synthesize scrollView = _scrollView;
@synthesize categoryMapping = _categoryMapping;

- (id)init {
  if ((self = [super init])) {
      //_categories = [[NSArray alloc] initWithObjects:@"music", @"food", @"book", @"film", @"other", nil];
      _categories = [[NSArray alloc] initWithObjects:@"places", @"books", @"music", @"movies", @"apps", nil];
      _categoryMapping = [[NSDictionary alloc] initWithObjectsAndKeys:
                          @"place", @"places",
                          @"book", @"books",
                          @"music", @"music",
                          @"film", @"movies",
                          @"app", @"apps",
                          nil];
      _buttons = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc {
    [_categories release], _categories=nil;
    [_categoryMapping release], _categoryMapping=nil;
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
        
        CGRect frame = CGRectMake(floorf(self.scrollView.frame.size.width - 58.0f), 4.0f, 50.0f, 44.0f);
        
        // close
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        [button setImage:[UIImage imageNamed:@"create_menu_close.png"] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        button.frame = frame;
        [_scrollView addSubview:button];
        [_buttons addObject:button];
        
        for (NSInteger i = 0; i < self.categories.count; i++) {
            
            frame.origin.y = floorf(frame.origin.y + 48.0f);
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
        
        frame.origin.y = floorf(frame.origin.y + 48.0f);

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
    [self slideIn];
}


#pragma mark - Animations

- (void)popInView1:(UIView*)view withDelay:(CGFloat)delay {
    
    [view.layer setValue:[NSNumber numberWithFloat:0.0f] forKeyPath:@"opacity"];
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.3f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut]];
    [CATransaction setCompletionBlock:^{
        [view.layer setValue:[NSNumber numberWithFloat:1.0f] forKeyPath:@"opacity"];
        [view.layer removeAllAnimations];
    }];
    
    CAAnimationGroup *groupAnimation = [CAAnimationGroup animation];
    groupAnimation.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
    groupAnimation.removedOnCompletion = NO;
    groupAnimation.fillMode = kCAFillModeForwards;
    
    CGPoint fromPos = view.layer.position;
    fromPos.y -= 10.0f;
    CABasicAnimation *position = [CABasicAnimation animationWithKeyPath:@"position"];
    position.fromValue = [NSValue valueWithCGPoint:fromPos];    
    
    CABasicAnimation *scale = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
    scale.fromValue = [NSNumber numberWithFloat:0.001f];
    scale.toValue = [NSNumber numberWithFloat:1.0f];
    
    CAKeyframeAnimation *opacity = [CAKeyframeAnimation animationWithKeyPath:@"opacity"];
    opacity.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.0f], nil];
    opacity.keyTimes = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:0.3f], [NSNumber numberWithFloat:1.0f], nil];
    
    CABasicAnimation *rotation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
    rotation.fromValue = [NSNumber numberWithFloat:0.0f];
    rotation.toValue = [NSNumber numberWithFloat:M_PI*2];
    
    [groupAnimation setAnimations:[NSArray arrayWithObjects:position, opacity, scale, rotation, nil]];
    [view.layer addAnimation:groupAnimation forKey:nil];
    
    [CATransaction commit];
    
}

- (void)popInView:(UIView*)view withDelay:(CGFloat)delay {
    
    [view.layer setValue:[NSNumber numberWithFloat:0.0f] forKeyPath:@"opacity"];

    [CATransaction begin];
    [CATransaction setAnimationDuration:0.2f];
    [CATransaction setAnimationTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut]];
    [CATransaction setCompletionBlock:^{
        [view.layer setValue:[NSNumber numberWithFloat:1.0f] forKeyPath:@"opacity"];
        [view.layer removeAllAnimations];
    }];
    
    CAAnimationGroup *groupAnimation = [CAAnimationGroup animation];
    groupAnimation.beginTime = [view.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
    groupAnimation.removedOnCompletion = NO;
    groupAnimation.fillMode = kCAFillModeForwards;
    
    CGPoint fromPos = view.layer.position;
    fromPos.x += 40.0f;
    CABasicAnimation *position = [CABasicAnimation animationWithKeyPath:@"position"];
    position.fromValue = [NSValue valueWithCGPoint:fromPos];

    CAKeyframeAnimation *opacity = [CAKeyframeAnimation animationWithKeyPath:@"opacity"];
    opacity.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.0f], nil];
    opacity.keyTimes = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:0.01f], [NSNumber numberWithFloat:1.0f], nil];

    [groupAnimation setAnimations:[NSArray arrayWithObjects:position, opacity, nil]];
    [view.layer addAnimation:groupAnimation forKey:nil];

    [CATransaction commit];
    
}

- (void)animateIn:(BOOL)animated {
    
    float delay = -.1f;
    NSInteger index = 0;
    for (UIView *view in _buttons) {
        
        if (index > 0) {
            if (animated) {
                [self popInView:view withDelay:delay];
            } else {
                [self popInView1:view withDelay:delay];
            }
            //double val = floorf(((double)arc4random() / 0x100000000) * 2.0f);
            // NSLog(@"%f", val);
            delay += animated ? 0.06f : 0.08f;
        } else {
            delay = 0.1f;
        }
        index ++;
        
    }
    
}

- (void)slideIn {
    
    [self animateIn:YES];
    
}

- (void)popIn {
    
    [self animateIn:NO];
    
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
    //Map to BE category strings
    category = [self.categoryMapping objectForKey:category];
    STEntitySearchController *controller = [[STEntitySearchController alloc] initWithCategory:category andQuery:nil];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [menuController pushViewController:controller animated:YES];
    
    /*
    if ([menuController.rootViewController isKindOfClass:[UINavigationController class]]) {
        [(UINavigationController*)menuController.rootViewController setNavigationBarHidden:YES animated:NO];
    }
     */
    
    [controller release];
    
}


@end
