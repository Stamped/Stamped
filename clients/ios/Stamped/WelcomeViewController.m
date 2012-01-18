//
//  WelcomeViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "WelcomeViewController.h"

#import <RestKit/RestKit.h>

#import "AccountManager.h"
#import "Util.h"
#import "FindFriendsViewController.h"
#import "Notifications.h"
#import "StampedAppDelegate.h"
#import "UserImageView.h"
#import "FindFriendsViewController.h"

static NSString* const kUpdateStampPath = @"/account/customize_stamp.json";
NSString* const kStampColors[7][2] = {
  { @"004ab2", @"0057d1" },
  { @"84004b", @"ff00ea" },
  { @"008000", @"36c339" },
  { @"ff7e00", @"ffea00" },
  { @"51c4bb", @"91ede8" },
  { @"42ff00", @"fc2599" },
  { @"5700ce", @"ff6000" }
};

@interface WelcomeViewController ()
- (void)setUserStampColorPrimary:(NSString*)primary secondary:(NSString*)secondary;

@property (nonatomic, retain) RKRequest* currentStampRequest;
@end

@implementation WelcomeViewController

@synthesize contentView = contentView_;
@synthesize scrollView = scrollView_;

@synthesize findFriendsNavigationController = findFriendsNavigationController_;

@synthesize userStampImageView = userStampImageView_;
@synthesize largeStampColorImageView = largeStampColorImageView_;
@synthesize userImageView = userImageView_;
@synthesize galleryStamp0 = galleryStamp0_;
@synthesize galleryStamp1 = galleryStamp1_;
@synthesize galleryStamp2 = galleryStamp2_;
@synthesize galleryStamp3 = galleryStamp3_;
@synthesize galleryStamp4 = galleryStamp4_;
@synthesize galleryStamp5 = galleryStamp5_;
@synthesize galleryStamp6 = galleryStamp6_;

@synthesize nextButton = nextButton_;
@synthesize backButton = backButton_;
@synthesize readyButton = readyButton_;

@synthesize page1Title = page1Title_;
@synthesize page2Title = page2Title_;
@synthesize page3Title = page3Title_;

@synthesize currentStampRequest = currentStampRequest_;

- (id)init {
  if ((self = [self initWithNibName:@"WelcomeView" bundle:nil])) {}
  return self;
}

- (void)dealloc {
  self.contentView = nil;
  self.scrollView = nil;
  self.page1Title = nil;
  self.page2Title = nil;
  self.page3Title = nil;
  self.galleryStamp0 = nil;
  self.galleryStamp1 = nil;
  self.galleryStamp2 = nil;
  self.galleryStamp3 = nil;
  self.galleryStamp4 = nil;
  self.galleryStamp5 = nil;
  self.galleryStamp6 = nil;
  self.nextButton = nil;
  self.backButton = nil;
  self.readyButton = nil;
  self.findFriendsNavigationController = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentStampRequest];
  self.currentStampRequest = nil;
  self.userStampImageView = nil;
  self.largeStampColorImageView = nil;
  self.userImageView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  backButton_.alpha = 0.0;
  readyButton_.alpha = 0.0;

  [self.scrollView addSubview:self.contentView];
  self.scrollView.contentSize = self.contentView.frame.size;

  UIFont* font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36.0];
  self.page1Title.font = font;
  self.page2Title.font = font;
  self.page3Title.font = font;
  
  for (NSUInteger i = 0; i < 7; ++i) {
    UIButton* galleryButton = [(UIButton*)self valueForKey:[NSString stringWithFormat:@"galleryStamp%d", i]];
    [galleryButton setBackgroundImage:[Util stampImageWithPrimaryColor:kStampColors[i][0]
                                                             secondary:kStampColors[i][1]]
                             forState:UIControlStateNormal];
  }
  User* currentUser = [AccountManager sharedManager].currentUser;
  self.userImageView.imageURL = [currentUser profileImageURLForSize:ProfileImageSize72];
  self.largeStampColorImageView.image = [Util gradientImage:largeStampColorImageView_.image
                                           withPrimaryColor:currentUser.primaryColor
                                                  secondary:currentUser.secondaryColor];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.contentView = nil;
  self.scrollView = nil;
  self.page1Title = nil;
  self.page2Title = nil;
  self.page3Title = nil;
  self.galleryStamp0 = nil;
  self.galleryStamp1 = nil;
  self.galleryStamp2 = nil;
  self.galleryStamp3 = nil;
  self.galleryStamp4 = nil;
  self.galleryStamp5 = nil;
  self.galleryStamp6 = nil;
  self.nextButton = nil;
  self.backButton = nil;
  self.readyButton = nil;
  self.findFriendsNavigationController = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentStampRequest];
  self.currentStampRequest = nil;
  self.largeStampColorImageView = nil;
  self.userStampImageView = nil;
  self.userImageView = nil;
}

#pragma mark - Private methods.

- (void)setUserStampColorPrimary:(NSString*)primary secondary:(NSString*)secondary {
  User* user = [AccountManager sharedManager].currentUser;
  user.primaryColor = primary;
  user.secondaryColor = secondary;
  UIImage* stampImage = [Util stampImageForUser:user];
  self.userStampImageView.image = stampImage;
  //user.stampImage = stampImage;
  [user.managedObjectContext save:NULL];
  [[NSNotificationCenter defaultCenter] postNotificationName:kCurrentUserHasUpdatedNotification
                                                      object:[AccountManager sharedManager]];
  self.largeStampColorImageView.image = [Util gradientImage:largeStampColorImageView_.image
                                           withPrimaryColor:primary
                                                  secondary:secondary];
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentStampRequest];
  self.currentStampRequest = nil;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUpdateStampPath 
                                                                    delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = mapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:primary, @"color_primary",
                                                                   secondary, @"color_secondary", nil];
  self.currentStampRequest = objectLoader;
  [objectLoader send];
}

#pragma mark - StampCustomizerViewDelegate methods.

- (void)stampCustomizer:(StampCustomizerViewController*)customizer
      chosePrimaryColor:(NSString*)primary
         secondaryColor:(NSString*)secondary {
  [self setUserStampColorPrimary:primary secondary:secondary];
}

#pragma mark - Actions

- (IBAction)backButtonPressed:(id)sender {
  CGPoint newOffset = CGPointMake(fmaxf(0, scrollView_.contentOffset.x - CGRectGetWidth(scrollView_.frame)), 0);
  [scrollView_ setContentOffset:newOffset animated:YES];
}

- (IBAction)nextButtonPressed:(id)sender {
  CGPoint newOffset = CGPointMake(fminf(scrollView_.contentSize.width - CGRectGetWidth(scrollView_.frame),
                                        scrollView_.contentOffset.x + CGRectGetWidth(scrollView_.frame)), 0);
  [scrollView_ setContentOffset:newOffset animated:YES];
}

- (IBAction)stampButtonPressed:(id)sender {
  UIButton* button = sender;
  for (UIView* view in [(UIView*)sender superview].subviews) {
    if ([view isMemberOfClass:[UIButton class]])
      [(UIButton*)view setSelected:NO];
    if ([view isMemberOfClass:[UIImageView class]] && view.hidden)
      view.hidden = NO;
  }
  button.selected = YES;
  // Make sure this is in sync with the nib. The white backgrounds are always one
  // index after the buttons themselves.
  NSUInteger index = [button.superview.subviews indexOfObject:button] + 1;
  if (index < button.superview.subviews.count) {
    UIView* whiteBackground = [button.superview.subviews objectAtIndex:index];
    whiteBackground.hidden = YES;
  }
  NSString* primary = kStampColors[button.tag][0];
  NSString* secondary = kStampColors[button.tag][1];
  userStampImageView_.image = [Util stampImageWithPrimaryColor:primary secondary:secondary];
  [self setUserStampColorPrimary:primary secondary:secondary];
}

- (IBAction)stampCustomizerButtonPressed:(id)sender {
  for (UIView* view in [(UIView*)sender superview].subviews) {
    if ([view isMemberOfClass:[UIButton class]])
      [(UIButton*)view setSelected:NO];
  }
  User* user = [AccountManager sharedManager].currentUser;
  StampCustomizerViewController* vc = [[StampCustomizerViewController alloc] initWithPrimaryColor:user.primaryColor
                                                                                        secondary:user.secondaryColor];
  vc.delegate = self;
  [self presentModalViewController:vc animated:YES];
  [vc release];
}

- (IBAction)findfromContacts:(id)sender {
  [((FindFriendsViewController*)[self.findFriendsNavigationController.viewControllers objectAtIndex:0]) findFromContacts:sender];
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)findFromTwitter:(id)sender {
  [((FindFriendsViewController*)[self.findFriendsNavigationController.viewControllers objectAtIndex:0]) findFromTwitter:sender];
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)findFromFacebook:(id)sender {
  [((FindFriendsViewController*)[self.findFriendsNavigationController.viewControllers objectAtIndex:0]) findFromFacebook:sender];
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)findFromStamped:(id)sender {
  [((FindFriendsViewController*)[self.findFriendsNavigationController.viewControllers objectAtIndex:0]) findFromStamped:sender];
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)dismissWelcomeView:(id)sender {
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadAllPanes object:nil];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[UIApplication sharedApplication].delegate;
  [delegate.navigationController dismissModalViewControllerAnimated:YES];
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  backButton_.alpha = fminf(1, scrollView_.contentOffset.x / CGRectGetWidth(scrollView_.frame));
  nextButton_.alpha = fmaxf(0, (scrollView_.contentSize.width - scrollView_.contentOffset.x - CGRectGetWidth(scrollView_.frame)) / CGRectGetWidth(scrollView_.frame));
  readyButton_.alpha = 1.0 - nextButton_.alpha;
}

@end