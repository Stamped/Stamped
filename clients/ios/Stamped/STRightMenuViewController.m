//
//  STRightMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRightMenuViewController.h"
#import "STViewContainer.h"
#import "Util.h"
#import "STButton.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import <QuartzCore/QuartzCore.h>
#import "STEntitySearchController.h"
#import "ECSlidingViewController.h"

@interface STRightMenuViewController ()

@property (nonatomic, readonly, retain) NSArray* categories;

@end

@implementation STRightMenuViewController

@synthesize categories = categories_;

- (id)init
{
  self = [super init];
  if (self) {
    categories_ = [[NSArray arrayWithObjects:
                           @"music",
                           @"food",
                           @"book",
                           @"film",
                           @"other",
                           nil] retain];
  }
  return self;
}

- (void)dealloc
{
  [categories_ release];
  [super dealloc];
}

- (void)buttonClicked:(STButton*)button {
  NSString* category = [self.categories objectAtIndex:button.tag];
  STEntitySearchController* controller = [[[STEntitySearchController alloc] initWithCategory:category andQuery:nil] autorelease];
  [self.slidingViewController resetTopViewWithAnimations:^{
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
  } onComplete:^{
  }];
}

- (void)loadView {
  UIScrollView* scroller = [[[UIScrollView alloc] initWithFrame:[Util standardFrameWithNavigationBar:NO]] autorelease];
  scroller.contentSize = CGSizeMake(scroller.frame.size.width, scroller.frame.size.height + 1);
  scroller.backgroundColor = [UIColor colorWithWhite:.3 alpha:1];
  STViewContainer* view = [[[STViewContainer alloc] initWithFrame:CGRectMake(0, 0, scroller.frame.size.width, 0)] autorelease];
  CGFloat buttonWidth = 70;
  CGFloat buttonPadding = ( scroller.frame.size.height - buttonWidth * self.categories.count ) / ( self.categories.count + 1);
  CGRect buttonFrame = CGRectMake(0, 0, buttonWidth, buttonWidth);
  
  for (NSInteger i = 0; i < self.categories.count; i++) {
    NSString* category = [self.categories objectAtIndex:i];
    UIView* views[2];
    for (NSInteger i = 0; i < 2; i++) {
      UIView* buttonView = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
      UIImage* image = [Util imageForCategory:category];
      UIImageView* imageView = [[[UIImageView alloc] initWithImage:image] autorelease];
      imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:buttonFrame];
      [buttonView addSubview:imageView];
      NSArray* colors;
      UIColor* borderColor;
      if (i == 0) {
        colors = [UIColor stampedGradient];
        borderColor = [UIColor stampedGrayColor];
      }
      else {
        colors = [UIColor stampedDarkGradient];
        borderColor = [UIColor stampedDarkGrayColor];
      }
      buttonView.layer.borderColor = borderColor.CGColor;
      buttonView.layer.borderWidth = 1;
      buttonView.layer.cornerRadius = 5;
      [Util addGradientToLayer:buttonView.layer withColors:colors vertical:YES];
      views[i] = buttonView;
    }
    STButton* button = [[[STButton alloc] initWithFrame:buttonFrame 
                                             normalView:views[0] 
                                             activeView:views[1] 
                                                 target:self 
                                              andAction:@selector(buttonClicked:)] autorelease];
    button.tag = i;
    NSLog(@"%f",[Util fullscreenFrame].size.width - buttonWidth);
    [Util reframeView:button withDeltas:CGRectMake([Util fullscreenFrame].size.width - buttonWidth, buttonPadding, 0, 0)];
    [view appendChildView:button];
  }
  [scroller addSubview:view];
  self.view = scroller;
}

- (void)viewDidLoad
{
  [super viewDidLoad];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
