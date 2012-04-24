//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import <Twitter/Twitter.h>

#import "AccountManager.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "STSynchronousWrapper.h"
#import "STEntityDetailFactory.h"
#import "STScrollViewContainer.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STStampDetailHeaderView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STStampedAPI.h"
#import "STStampDetailCommentsView.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"
#import "STStampedAPI.h"
#import "STButton.h"

@interface STStampDetailToolbar : UIView

- (id)initWithParent:(UIView*)view andStamp:(id<STStamp>)stamp;
- (void)toggleToolbar:(id)button;

@property (nonatomic, readonly, retain) NSArray* buttons;
@property (nonatomic, readwrite, assign) BOOL expanded;
@property (nonatomic, readonly, retain) UIView* expandButton;
@property (nonatomic, readonly, retain) UIView* buttonContainer;

@end

@implementation STStampDetailToolbar

@synthesize buttons = buttons_;
@synthesize expanded = expanded_;
@synthesize expandButton = expandButton_;
@synthesize buttonContainer = buttonContainer_;

- (id)initWithParent:(UIView*)view andStamp:(id<STStamp>)stamp {
  CGFloat xPadding = 5;
  CGFloat yPadding = 10;
  CGFloat height = 40;
  CGRect frame = CGRectMake(xPadding, view.frame.size.height - (height + yPadding), view.frame.size.width - (2 * xPadding), height);
  self = [super initWithFrame:frame];
  if (self) {
    expanded_ = YES;
    self.layer.cornerRadius = 5;
    self.layer.shadowOpacity = .3;
    self.layer.shadowRadius = 3;
    self.layer.shadowOffset = CGSizeMake(0, 2);
    self.layer.borderColor = [UIColor colorWithWhite:89.0/255 alpha:1].CGColor;
    self.layer.borderWidth = 1;
    [Util addGradientToLayer:self.layer 
                  withColors:[NSArray arrayWithObjects:
                              [UIColor colorWithWhite:.4 alpha:1],
                              [UIColor colorWithWhite:.2 alpha:1],
                              nil] 
                    vertical:YES];
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"toolbar_todoButton"]] autorelease];
    UIImageView* imageView2 = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"toolbar_todoButton"]] autorelease];
    expandButton_ = [[STButton alloc] initWithFrame:imageView.frame 
                                         normalView:imageView 
                                         activeView:imageView2 
                                             target:self 
                                          andAction:@selector(toggleToolbar:)];
    [Util reframeView:expandButton_ withDeltas:CGRectMake(frame.size.width - (expandButton_.frame.size.width - 0), 0, 0, 0)];
    
    
    buttons_ = [[NSMutableArray arrayWithObjects:
                 [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                 [[[STTodoButton alloc] initWithStamp:stamp] autorelease],
                 [[[STStampButton alloc] initWithStamp:stamp] autorelease],
                 [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                 [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                 nil] retain];
    CGFloat buttonSpacing = 50;
    buttonContainer_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, CGRectGetMinX(expandButton_.frame)+50, frame.size.height-10)];
    for (NSInteger i = 0; i < buttons_.count; i++) {
      UIView* button = [buttons_ objectAtIndex:i];
      [Util reframeView:button withDeltas:CGRectMake(-5 + (i * buttonSpacing), 0, 0, 0)];
      [buttonContainer_ addSubview:button];
    }
    buttonContainer_.clipsToBounds = YES;
    [self addSubview:buttonContainer_];
    self.clipsToBounds = YES;
    [self addSubview:expandButton_];
  }
  return self;
}

- (void)toggleToolbar:(id)button {
  CGFloat delta = 155;
  CGFloat deltaSpacing = 15;
  CGFloat duration = .5;
  if (self.expanded) {
    [UIView animateWithDuration:duration animations:^{
      [Util reframeView:self withDeltas:CGRectMake(delta, 0, -delta, 0)];
      [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, -delta, 0)];
      [Util reframeView:self.expandButton withDeltas:CGRectMake(-delta, 0, 0, 0)];
      for (NSInteger i = 0; i < buttons_.count; i++) {
        UIView* button = [buttons_ objectAtIndex:i];
        [Util reframeView:button withDeltas:CGRectMake(i * -deltaSpacing, 0, 0, 0)];
        if (CGRectGetMaxX(button.frame) - 20 > self.buttonContainer.frame.size.width - 50) {
          button.alpha = 0;
        }
      }
    }];
  }
  else {
    [UIView animateWithDuration:duration animations:^{
      [Util reframeView:self withDeltas:CGRectMake(-delta, 0, delta, 0)];
      [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, delta, 0)];
      [Util reframeView:self.expandButton withDeltas:CGRectMake(delta, 0, 0, 0)];
      for (NSInteger i = 0; i < buttons_.count; i++) {
        UIView* button = [buttons_ objectAtIndex:i];
        [Util reframeView:button withDeltas:CGRectMake(i * deltaSpacing, 0, 0, 0)];
        button.alpha = 1;
      }
    }];
  }
  self.expanded = !self.expanded;
}

- (void)reloadStampedData {
  for (id view in self.buttonContainer.subviews) {
    if ([view respondsToSelector:@selector(reloadStampedData)]) {
      [view reloadStampedData]; 
    }
  }
}

@end

@interface STStampDetailViewController () <UIActionSheetDelegate, UITextFieldDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;
- (void)_deleteStampButtonPressed:(id)caller;

@property (nonatomic, readonly, retain) STStampDetailHeaderView* headerView;
@property (nonatomic, readonly, retain) STStampDetailCommentsView* commentsView;

@end

@implementation STStampDetailViewController

@synthesize headerView = _headerView;
@synthesize commentsView = _commentsView;
@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)viewDidLoad {
  //STToolbarView* toolbar = [[STToolbarView alloc] init];
  //_toolbar = toolbar;
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:self.stamp.entity.title]
                                                                  style:UIBarButtonItemStyleBordered
                                                                 target:nil
                                                                 action:nil] autorelease];
  [[self navigationItem] setBackBarButtonItem:backButton];
  
  _headerView = [[STStampDetailHeaderView alloc] initWithStamp:self.stamp];
  [self.scrollView appendChildView:_headerView];
  _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp andDelegate:self.scrollView];
  _commentsView.addCommentView.delegate = self;
  [self.scrollView appendChildView:_commentsView];
  
  NSMutableArray* views = [NSMutableArray arrayWithObjects:
                           [[[STLikeButton alloc] initWithStamp:self.stamp] autorelease],
                           [[[STTodoButton alloc] initWithStamp:self.stamp] autorelease],
                           nil];
  if (![AccountManager.sharedManager.currentUser.screenName isEqualToString:self.stamp.user.screenName]) {
    [views addObject:[[[STStampButton alloc] initWithStamp:self.stamp] autorelease]];
  }
  else {
    UIBarButtonItem* rightButton = [[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                    style:UIBarButtonItemStylePlain
                                                                   target:self
                                                                   action:@selector(_deleteStampButtonPressed:)];
    self.navigationItem.rightBarButtonItem = rightButton;
  }
  //[toolbar packViews:views];
  UIView* newToolbar = [[[STStampDetailToolbar alloc] initWithParent:self.view andStamp:self.stamp] autorelease];
  [self.view addSubview:newToolbar];
  
  [[STStampedAPI sharedInstance] entityDetailForEntityID:self.stamp.entity.entityID andCallback:^(id<STEntityDetail> detail, NSError* error) {
    STSynchronousWrapper* wrapper = [STSynchronousWrapper wrapperForStampDetail:detail withFrame:CGRectMake(0, 0, 320, 200) stamp:self.stamp delegate:self.scrollView];
    [self.scrollView appendChildView:wrapper];
    self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width, self.scrollView.contentSize.height);
    UIView* padding = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 50)] autorelease];
    [self.scrollView appendChildView:padding];
  }];
}

- (void)viewDidUnload {
  [_toolbar release];
  [_headerView release];
}

- (void)dealloc {
  [_stamp release];
  [super dealloc];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  NSLog(@"viewWillDisappear");
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  //[self setUpToolbar];
  [_headerView setNeedsDisplay];
  NSLog(@"viewWillAppear");
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  //stampPhotoView_.imageURL = stamp_.imageURL;
}

- (void)_deleteStampButtonPressed:(id)caller {
  [Util confirmWithMessage:@"Are you sure?" action:@"Delete" destructive:YES withBlock:^(BOOL confirmed) {
    if (confirmed) {
      STActionContext* context = [STActionContext contextWithCompletionBlock:^(id success, NSError *error) {
        if (!error) {
          [[Util sharedNavigationController] popViewControllerAnimated:YES];
        }
      }];
      id<STAction> action = [STStampedActions actionDeleteStamp:self.stamp.stampID withOutputContext:context];
      [[STActionManager sharedActionManager] didChooseAction:action withContext:context];    }
  }];
}

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail {
  NSLog(@"detail");
  CGFloat wrapperHeight = 200;
  CGRect wrapperFrame = CGRectMake(0, 0 , 320, wrapperHeight);
  STSynchronousWrapper* eDetailView = [STSynchronousWrapper wrapperForEntityDetail:detail
                                                                         withFrame:wrapperFrame 
                                                                          andStyle:@"StampDetail" 
                                                                          delegate:self.scrollView];
  [self.scrollView appendChildView:eDetailView];
}

- (void)handleEntityTap:(id)sender {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entity.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (UIView *)toolbar {
  return _toolbar;
}

@end
