//
//  STEntitySearchController.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySearchController.h"
#import "Util.h"
#import "STSearchField.h"
#import "UIButton+Stamped.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "CALayer+Stamped.h"
#import "STButton.h"
#import "STStampedAPI.h"

@interface STEntitySearchController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* initialQuery;

@end

@implementation STEntitySearchController

@synthesize category = category_;
@synthesize initialQuery = initialQuery_;

- (id)initWithCategory:(NSString*)category andQuery:(NSString*)query {
  self = [super init];
  if (self) {
    category_ = [category retain];
    initialQuery_ = [query retain];
    [[STStampedAPI sharedInstance] en
  }
  return self;
}

- (void)dealloc
{
  [category_ release];
  [initialQuery_ release];
  [super dealloc];
}

- (void)cancelClicked {
  [[Util sharedNavigationController] popViewControllerAnimated:YES];
}

- (void)loadView {
  self.view = [[[UIView alloc] initWithFrame:[Util standardFrameWithNavigationBar:NO]] autorelease];
  UIView* header = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, 40)] autorelease];
  [Util addGradientToLayer:header.layer 
                withColors:[NSArray arrayWithObjects:[UIColor colorWithWhite:.95 alpha:1], [UIColor colorWithWhite:.9 alpha:1], nil] 
                  vertical:YES];
  STSearchField* searchField = [[[STSearchField alloc] init] autorelease];
  if (self.initialQuery) {
    searchField.text = self.initialQuery;
  }
  searchField.enablesReturnKeyAutomatically = NO;
  searchField.frame = [Util centeredAndBounded:searchField.frame.size inFrame:header.frame];
  CGFloat xPadding = 5;
  CGFloat buttonWidth = 60;
  [Util reframeView:searchField withDeltas:CGRectMake(xPadding, 0, -(xPadding * 3 + buttonWidth), 0)];
  [header addSubview:searchField];
  
  CGRect cancelFrame = [Util centeredAndBounded:CGSizeMake(buttonWidth, searchField.frame.size.height) 
                                        inFrame:CGRectMake(CGRectGetMaxX(searchField.frame) + xPadding, 0, buttonWidth, header.frame.size.height)];
  UIView* cancelViews[2];
  for (NSInteger i = 0; i < 2; i++) {
    UIView* cancelView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, cancelFrame.size.width, cancelFrame.size.height)] autorelease];
    UILabel* label = [Util viewWithText:@"Cancel"
                                   font:[UIFont stampedFontWithSize:14]
                                  color:i == 0 ? [UIColor stampedGrayColor] : [UIColor whiteColor]
                                   mode:UILineBreakModeClip
                             andMaxSize:cancelFrame.size];
    label.frame = [Util centeredAndBounded:label.frame.size inFrame:cancelView.frame];
    [cancelView addSubview:label];
    if (i == 0) {
      [cancelView.layer useStampedButtonNormalStyle];
    }
    else {
      [cancelView.layer useStampedButtonActiveStyle];
    }
    cancelViews[i] = cancelView;
  }
  STButton* cancelButton = [[[STButton alloc] initWithFrame:cancelFrame 
                                                 normalView:cancelViews[0] 
                                                 activeView:cancelViews[1] 
                                                     target:self 
                                                  andAction:@selector(cancelClicked)] autorelease];
  [header addSubview:cancelButton];
  
  
  UIView* tableView = [[[UITableView alloc] initWithFrame:CGRectMake(0, 
                                                                     CGRectGetMaxY(header.frame), 
                                                                     self.view.frame.size.width, 
                                                                     self.view.frame.size.height - CGRectGetMaxY(header.frame))] autorelease];
  //tableView.backgroundColor = [UIColor grayColor];
  [self.view addSubview:tableView];
  [self.view addSubview:header];
}

- (void)willMoveToParentViewController:(UIViewController *)parent {
  if (parent) {
    [Util sharedNavigationController].navigationBarHidden = YES;
  }
  else {
    [Util sharedNavigationController].navigationBarHidden = NO;
  }
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  return nil;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {

}

@end
