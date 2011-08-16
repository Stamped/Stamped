//
//  PeopleViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

static NSString* const kFriendsPath = @"/friendships/friends";
static NSString* const kFollowersPath = @"/friendships/friends";
static const NSInteger kFriendsSection = 0;
static const NSInteger kFollowersSection = 1;

@interface SectionHeaderView : UIView
@property (nonatomic, readonly) UILabel* leftLabel;
@property (nonatomic, readonly) UILabel* rightLabel;
@end

@implementation SectionHeaderView

@synthesize leftLabel = leftLabel_;
@synthesize rightLabel = rightLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
    gradientLayer.frame = frame;
    gradientLayer.colors =
        [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.88 alpha:1.0].CGColor,
                                  (id)[UIColor colorWithWhite:0.95 alpha:1.0].CGColor, nil];
    [self.layer addSublayer:gradientLayer];
    [gradientLayer release];
    
    leftLabel_ = [[UILabel alloc] initWithFrame:CGRectOffset(frame, 9, 0)];
    leftLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    leftLabel_.shadowColor = [UIColor whiteColor];
    leftLabel_.shadowOffset = CGSizeMake(0, 1);
    leftLabel_.textColor = [UIColor stampedGrayColor];
    leftLabel_.backgroundColor = [UIColor clearColor];
    [self addSubview:leftLabel_];
    [leftLabel_ release];
    
    rightLabel_ = [[UILabel alloc] initWithFrame:CGRectOffset(frame, -9, 0)];
    rightLabel_.textAlignment = UITextAlignmentRight;
    rightLabel_.textColor = [UIColor stampedGrayColor];
    rightLabel_.shadowColor = [UIColor whiteColor];
    rightLabel_.shadowOffset = CGSizeMake(0, 1);
    rightLabel_.backgroundColor = [UIColor clearColor];
    rightLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self addSubview:rightLabel_];
    [rightLabel_ release];
    
    UIView* bottomBorder = [[UIView alloc] initWithFrame:frame];
    bottomBorder.backgroundColor = [UIColor colorWithWhite:0.88 alpha:1.0];
    CGRect bottomBorderFrame = frame;
    bottomBorderFrame.size.height = 1;
    bottomBorderFrame.origin.y = CGRectGetHeight(frame) - 1;
    bottomBorder.frame = bottomBorderFrame;
    [self addSubview:bottomBorder];
    [bottomBorder release];
    
  }
  return self;
}

@end

@interface PeopleViewController ()
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)loadFriendsFromNetwork;
- (void)loadFriendsFromDataStore;

@property (nonatomic, copy) NSArray* followers;
@property (nonatomic, copy) NSArray* friends;
@end

@implementation PeopleViewController

@synthesize currentUserView = currentUserView_;
@synthesize userStampImageView = userStampImageView_;
@synthesize userFullNameLabel = userFullNameLabel_;
@synthesize userScreenNameLabel = userScreenNameLabel_;
@synthesize addFriendsButton = addFriendsButton_;
@synthesize followers = followers_;
@synthesize friends = friends_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(currentUserUpdated:)
                                               name:kCurrentUserHasUpdatedNotification
                                             object:[AccountManager sharedManager]];
  
  userScreenNameLabel_.textColor = [UIColor lightGrayColor];
  userFullNameLabel_.textColor = [UIColor stampedBlackColor];
  [self loadFriendsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)userPulledToReload {
  [self setIsLoading:NO];
}

- (void)currentUserUpdated:(NSNotification*)notification {
  User* currentUser = [AccountManager sharedManager].currentUser;
  currentUserView_.imageURL = currentUser.profileImageURL;
  userStampImageView_.image = currentUser.stampImage;
  userScreenNameLabel_.text = currentUser.screenName;
  userFullNameLabel_.text = [NSString stringWithFormat:@"%@ %@", currentUser.firstName, currentUser.lastName];
}

- (void)loadFriendsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  NSString* authToken = [AccountManager sharedManager].authToken.accessToken;
  NSDictionary* params = [NSDictionary dictionaryWithObject:authToken forKey:@"oauth_token"];
  [[RKClient sharedClient] get:kFriendsPath
                   queryParams:params
                      delegate:self];
}

- (void)loadFriendsFromDataStore {
  
}

#pragma mark - RKRequestDelegate Methods.

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  NSLog(@"Problem loading stuff. Error: %@", [error localizedDescription]);
}

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  //NSError* error;
  //id json = [response parsedBody:error];
  NSLog(@"json response: %@", response.bodyAsString);
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  // Two. Followers and following.
  return 2;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 50;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
  }

  // Configure the cell...

  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  SectionHeaderView* view = [[SectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)];
  view.backgroundColor = [UIColor blueColor];
  view.leftLabel.text = section == 0 ? @"Following" : @"Followers";
  view.rightLabel.text =
      [NSString stringWithFormat:@"%u", section == kFriendsSection ? [friends_ count] : [followers_ count]];
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  // Navigation logic may go here. Create and push another view controller.
  /*
   <#DetailViewController#> *detailViewController = [[<#DetailViewController#> alloc] initWithNibName:@"<#Nib name#>" bundle:nil];
   // ...
   // Pass the selected object to the new view controller.
   [self.navigationController pushViewController:detailViewController animated:YES];
   [detailViewController release];
   */
}

@end
