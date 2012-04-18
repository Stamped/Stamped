//
//  SharingSettingsViewController.m
//  Stamped
//
//  Created by Jake Zien on 10/31/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "SharingSettingsViewController.h"
#import "SocialManager.h"

@interface SharingSettingsViewController ()

-(void)updateUI;

@end

@implementation SharingSettingsViewController

@synthesize twitterIconView;
@synthesize fbIconView;
@synthesize twitterConnectButton;
@synthesize fbConnectButton;
@synthesize twitterLabel;
@synthesize fbLabel;
@synthesize twitterNameLabel;
@synthesize fbNameLabel;
@synthesize scrollView;

#pragma mark - View lifecycle

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];  self.twitterIconView = nil;
  self.fbIconView = nil;
  self.twitterConnectButton = nil;
  self.fbConnectButton = nil;
  self.twitterLabel = nil;
  self.fbLabel = nil;
  self.twitterNameLabel = nil;
  self.fbNameLabel = nil;
  self.scrollView = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Sharing"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];

  self.scrollView.contentSize = CGSizeMake(self.scrollView.bounds.size.width, self.scrollView.bounds.size.height + 1);
  [super viewDidLoad];
  
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(updateUI)
                                               name:kSocialNetworksChangedNotification
                                             object:nil];
}

- (void)viewDidUnload {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.twitterIconView = nil;
  self.fbIconView = nil;
  self.twitterConnectButton = nil;
  self.fbConnectButton = nil;
  self.twitterLabel = nil;
  self.fbLabel = nil;
  self.twitterNameLabel = nil;
  self.fbNameLabel = nil;
  self.scrollView = nil;
  [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
  //self.navigationController.navigationBarHidden = YES;
  [self updateUI];
  [super viewWillAppear:animated];
}

#pragma mark - Actions

- (IBAction)twitterButtonPressed:(id)sender {
  if (self.twitterConnectButton.isSelected) {
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure you want to disconnect from Twitter?"
                                                        delegate:self
                                               cancelButtonTitle:@"Cancel"
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Disconnect", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:self.view];
  } else {
    [[SocialManager sharedManager] signInToTwitter:self.navigationController];
  }
}

- (IBAction)fbButtonPressed:(id)sender {
  if (self.fbConnectButton.isSelected) {
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure you want to disconnect from Facebook?"
                                                        delegate:self
                                               cancelButtonTitle:@"Cancel"
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Disconnect", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:self.view];
  } else {
    [[SocialManager sharedManager] signInToFacebook];
  }
}

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

#pragma mark - Private

- (void)updateUI {
  if ([[SocialManager sharedManager] isSignedInToTwitter]) {
    CGRect frame = self.twitterConnectButton.frame;
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      self.twitterConnectButton.selected = YES;
      [self.twitterConnectButton setImage:[UIImage imageNamed:@"settings_sharing_button_disconnect"]
                                 forState:UIControlStateNormal];
      self.twitterConnectButton.frame = CGRectMake(210, frame.origin.y, 90, frame.size.height);
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_on"];
      NSString* name = [[NSUserDefaults standardUserDefaults] objectForKey:@"TwitterUsername"];
      if (name) {
        self.twitterLabel.frame = CGRectMake(53, 29, 138, 21);
        if (![self.twitterNameLabel.text isEqualToString:name])
          self.twitterNameLabel.text = name;
        self.twitterNameLabel.alpha = 1.0;
      }
    }
    completion:nil];
  } else {
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.twitterConnectButton.frame;
      self.twitterConnectButton.selected = NO;
      [self.twitterConnectButton setImage:[UIImage imageNamed:@"settings_sharing_button_connect"]
                                 forState:UIControlStateNormal];
      self.twitterLabel.frame = CGRectMake(53, 37, 138, 21);
      self.twitterNameLabel.alpha = 0.0;
      self.twitterConnectButton.frame = CGRectMake(225, frame.origin.y, 75, frame.size.height);
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_off"];
    }
    completion:nil];
  }

  if ([[SocialManager sharedManager] isSignedInToFacebook]) {
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.fbConnectButton.frame;
      self.fbConnectButton.selected = YES;
      [self.fbConnectButton setImage:[UIImage imageNamed:@"settings_sharing_button_disconnect"]
                            forState:UIControlStateNormal];
      self.fbConnectButton.frame = CGRectMake(210, frame.origin.y, 90, frame.size.height);
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_on"];
      NSString* name = [[NSUserDefaults standardUserDefaults] objectForKey:@"FBName"];
      if (name) {
        self.fbLabel.frame = CGRectMake(53, 102, 138, 21);
        if (![self.fbNameLabel.text isEqualToString:name])
          self.fbNameLabel.text = name;
        self.fbNameLabel.alpha = 1.0;
      }
    }
    completion:nil];
  } else {    
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.fbConnectButton.frame;
      self.fbConnectButton.selected = NO;
      [self.fbConnectButton setImage:[UIImage imageNamed:@"settings_sharing_button_connect"]
                            forState:UIControlStateNormal];
      self.fbConnectButton.frame = CGRectMake(225, frame.origin.y, 75, frame.size.height);
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_off"];
      self.fbLabel.frame = CGRectMake(53, 110, 138, 21);
      self.fbNameLabel.alpha = 0.0;
    }
    completion:nil];
  }
}

#pragma mark - UIActionSheetDelegate methods

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 0) {
    if ([actionSheet.title rangeOfString:@"Twitter"].location != NSNotFound)
      [[SocialManager sharedManager] signOutOfTwitter:YES];
    else if ([actionSheet.title rangeOfString:@"Facebook"].location != NSNotFound)
      [[SocialManager sharedManager] signOutOfFacebook:YES];
  }
}



@end
