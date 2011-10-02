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
@synthesize userImageView = userImageView_;
@synthesize galleryStamp0 = galleryStamp0_;
@synthesize galleryStamp1 = galleryStamp1_;
@synthesize galleryStamp2 = galleryStamp2_;
@synthesize galleryStamp3 = galleryStamp3_;
@synthesize galleryStamp4 = galleryStamp4_;
@synthesize galleryStamp5 = galleryStamp5_;
@synthesize galleryStamp6 = galleryStamp6_;

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
  self.findFriendsNavigationController = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentStampRequest];
  self.currentStampRequest = nil;
  self.userStampImageView = nil;
  self.userImageView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

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
  self.userImageView.imageURL = [AccountManager sharedManager].currentUser.profileImageURL;
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
  self.findFriendsNavigationController = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentStampRequest];
  self.currentStampRequest = nil;
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
  user.stampImage = stampImage;
  [user.managedObjectContext save:NULL];
  [[NSNotificationCenter defaultCenter] postNotificationName:kCurrentUserHasUpdatedNotification
                                                      object:[AccountManager sharedManager]];
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

- (IBAction)stampButtonPressed:(id)sender {
  UIButton* button = sender;
  for (UIView* view in [(UIView*)sender superview].subviews) {
    if ([view isMemberOfClass:[UIButton class]])
      [(UIButton*)view setSelected:NO];
  }
  button.selected = YES;
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
  StampCustomizerViewController* vc = [[StampCustomizerViewController alloc] initWithNibName:@"StampCustomizerViewController" bundle:nil];
  vc.delegate = self;
  [self presentModalViewController:vc animated:YES];
  [vc release];
}

- (IBAction)findfromContacts:(id)sender {  
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)findFromTwitter:(id)sender {
  [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
}

- (IBAction)dismissWelcomeView:(id)sender {
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadAllPanes object:nil];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[UIApplication sharedApplication].delegate;
  [delegate.navigationController dismissModalViewControllerAnimated:YES];
}

@end
