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

@implementation SettingsViewController

@synthesize scrollView = scrollView_;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIView* lastView = scrollView_.subviews.lastObject;
  scrollView_.contentSize = CGSizeMake(320, CGRectGetMaxY(lastView.frame) + 30);
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Custom methods.

- (IBAction)doneButtonPressed:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
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
  SharingSettingsViewController* vc = [[SharingSettingsViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (IBAction)aboutUsButtonPressed:(id)sender {
  AboutUsViewController* vc = [[AboutUsViewController alloc] init];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (IBAction)logoutButtonPressed:(id)sender {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Logout"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
}



#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 0) {  // Logout.
    [self.parentViewController dismissModalViewControllerAnimated:NO];
    [[AccountManager sharedManager] logout];
  }
}

@end
