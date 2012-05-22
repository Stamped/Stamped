//
//  SettingsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SettingsViewController.h"

#import "AccountManager.h"
#import "EditProfileViewController.h"
#import "SharingSettingsViewController.h"
#import "AboutUsViewController.h"
#import "WebViewController.h"
#import "TOSViewController.h"
#import "ECSlidingViewController.h"
#import "Util.h"

@implementation SettingsViewController

@synthesize scrollView = scrollView_;
@synthesize contentView = contentView;
@synthesize sharingView = sharingView_;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (id)init {
  return [self initWithNibName:@"SettingsViewController" bundle:nil];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.scrollView = nil;
  self.contentView = nil;
  self.sharingView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)backButtonClicked:(id)button {
  [self.slidingViewController anchorTopViewTo:ECRight];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [scrollView_ addSubview:self.contentView];
  scrollView_.contentSize = self.contentView.bounds.size;
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Settings"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
    [Util addHomeButtonToController:self withBadge:YES];
}

- (void)viewDidUnload {
  self.scrollView = nil;
  self.contentView = nil;
  self.sharingView = nil;
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Custom methods.

- (IBAction)doneButtonPressed:(id)sender {
  //[[STRootMenuView sharedInstance] toggle];
  //[self.presentingViewController dismissModalViewControllerAnimated:YES];
}


- (IBAction)editProfileButtonPressed:(id)sender {
  EditProfileViewController* vc = [[EditProfileViewController alloc] init];
  vc.user = [AccountManager sharedManager].currentUser;
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}


- (IBAction)notificationsButtonPressed:(id)sender {
//  NotificationSettingsViewController* vc = [[NotificationSettingsViewController alloc] init];
//  [self.navigationController pushViewController:vc animated:YES];
//  [vc release];
}

- (IBAction)sharingButtonPressed:(id)sender {
  if (!sharingView_) {
    SharingSettingsViewController* vc = [[SharingSettingsViewController alloc] init];
    self.sharingView = vc;
    [vc release];
  }
  [self.navigationController pushViewController:self.sharingView animated:YES];
}

- (IBAction)aboutUsButtonPressed:(id)sender {
  AboutUsViewController* vc = [[AboutUsViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (IBAction)FAQButtonPressed:(id)sender {
  WebViewController* vc = [[WebViewController alloc] initWithURL:[NSURL URLWithString:@"http://www.stamped.com/faq-mobile.html/"]];
  [self.navigationController pushViewController:vc animated:YES];
  [vc hideToolbar:YES];
  [vc release];
}

- (IBAction)logoutButtonPressed:(id)sender {
  NSLog(@"asdklfjafdjkl");
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Logout"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
}

- (IBAction)legalButtonPressed:(id)sender {
  TOSViewController* vc = [[TOSViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  vc.doneButton.hidden = YES;
  [vc release];
}

- (IBAction)feedbackButtonPressed:(id)sender {
  WebViewController* vc = [[WebViewController alloc] initWithURL:[NSURL URLWithString:@"http://www.stamped.com/feedback-mobile.html/"]];
  [self.navigationController pushViewController:vc animated:YES];
  vc.webView.scalesPageToFit = YES;
  vc.shareButton.hidden = YES;
  [vc release];
}


#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 0) {  // Logout.
    [self.parentViewController dismissModalViewControllerAnimated:NO];
    [[AccountManager sharedManager] logout];
  }
}

@end
