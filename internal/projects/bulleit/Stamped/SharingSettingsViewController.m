//
//  SharingSettingsViewController.m
//  Stamped
//
//  Created by Jake Zien on 10/31/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "SharingSettingsViewController.h"
#import "StampedAppDelegate.h"

@interface SharingSettingsViewController ()

@property (nonatomic, retain) Facebook* fbClient;

-(void)setButton:(UIButton *)button connected:(BOOL)connected;
-(void)updateUI;
- (void)signInToFacebook;

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

@synthesize fbClient = fbClient_;

//- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
//{
//    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
//    if (self) {
//        // Custom initialization
//    }
//    return self;
//}

//- (void)didReceiveMemoryWarning
//{
//    // Releases the view if it doesn't have a superview.
//    [super didReceiveMemoryWarning];
//    
//    // Release any cached data, images, etc that aren't in use.
//}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  self.navigationItem.title = @"Sharing";
  [super viewDidLoad];
}

- (void)viewDidUnload {
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self updateUI];
  [super viewWillAppear:animated];
}

#pragma mark - Actions

- (IBAction)twitterButtonPressed:(id)sender {
  [self updateUI];
}

- (IBAction)fbButtonPressed:(id)sender {
  [self updateUI];
}

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

#pragma mark - Facebook

- (void)signInToFacebook {
  if (!self.fbClient.isSessionValid) {
    self.fbClient.sessionDelegate = self;
    [self.fbClient authorize:[[NSArray alloc] initWithObjects:@"offline_access", nil]];
  }
}


#pragma mark - Private

- (void)updateUI {
  // Check for a valid FB session before updating.
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.fbClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.fbClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  
  if (self.fbClient.isSessionValid) {
    CGRect frame = self.fbConnectButton.frame;
    self.fbConnectButton.imageView.image = [UIImage imageNamed:@"settings_sharing_button_disconnect"];
    self.fbConnectButton.frame = CGRectMake(210, frame.origin.y, 90, frame.size.height);
    self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_on"];
  }
  else {
    CGRect frame = self.fbConnectButton.frame;
    self.fbConnectButton.imageView.image = [UIImage imageNamed:@"settings_sharing_button_connect"];
    self.fbConnectButton.frame = CGRectMake(225, frame.origin.y, 75, frame.size.height);
    self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_off"];
  }
}


- (void)setButton:(UIButton *)button connected:(BOOL)connected {
  UIImage* connectImg = [UIImage imageNamed:@"settings_sharing_button_connect"];
  UIImage* disconnectImg = [UIImage imageNamed:@"settings_sharing_button_disconnect"];
  
  if (connected) {
    button.imageView.image = disconnectImg;
    CGRect frame = button.frame;
    frame.size.width = disconnectImg.size.width;
    frame.origin.x -= disconnectImg.size.width - connectImg.size.width;
    button.frame = frame;
    if ([button isEqual:self.twitterConnectButton])
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_on"];
    else if ([button isEqual:self.fbConnectButton])
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_on"];                                    
  }
  else {
    button.imageView.image = connectImg;
    CGRect frame = button.frame;
    frame.size.width = connectImg.size.width;
    frame.origin.x += disconnectImg.size.width - connectImg.size.width;
    button.frame = frame;
    if ([button isEqual:self.twitterConnectButton])
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_off"];
    else if ([button isEqual:self.fbConnectButton])
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_off"];
  }
}

@end
