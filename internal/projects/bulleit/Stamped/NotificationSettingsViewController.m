//
//  NotificationSettingsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/2/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "NotificationSettingsViewController.h"

static NSString* const kSettingsHaveBeenSetKey = @"settings_have_been_set";

static NSString* const kPushCreditKey = @"ios_alert_credit";
static NSString* const kPushLikeKey = @"ios_alert_like";
static NSString* const kPushFavoriteKey = @"ios_alert_fav";
static NSString* const kPushMentionKey = @"ios_alert_mention";
static NSString* const kPushCommentKey = @"ios_alert_comment";
static NSString* const kPushReplyKey = @"ios_alert_reply";
static NSString* const kPushFollowKey = @"ios_alert_follow";
static NSString* const kEmailCreditKey = @"email_alert_credit";
static NSString* const kEmailLikeKey = @"email_alert_like";
static NSString* const kEmailFavoriteKey = @"email_alert_fav";
static NSString* const kEmailMentionKey = @"email_alert_mention";
static NSString* const kEmailCommentKey = @"email_alert_comment";
static NSString* const kEmailReplyKey = @"email_alert_reply";
static NSString* const kEmailFollowKey = @"email_alert_follow";

@interface NotificationSettingsViewController ()
- (void)syncInterfaceFromPrefs;
@end

@implementation NotificationSettingsViewController

@synthesize scrollView = scrollView_;
@synthesize creditPushSwitch = creditPushSwitch_;
@synthesize likePushSwitch = likePushSwitch_;
@synthesize favoritePushSwitch = favoritePushSwitch_;
@synthesize mentionPushSwitch = mentionPushSwitch_;
@synthesize commentPushSwitch = commentPushSwitch_;
@synthesize replyPushSwitch = replyPushSwitch_;
@synthesize followPushSwitch = followPushSwitch_;

- (id)init {
  self = [self initWithNibName:@"NotificationSettingsViewController" bundle:nil];
  if (self) {}
  return self;
}

- (void)dealloc {
  self.scrollView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIView* lastView = scrollView_.subviews.lastObject;
  scrollView_.contentSize = CGSizeMake(320, CGRectGetMaxY(lastView.frame));
  if (![[NSUserDefaults standardUserDefaults] boolForKey:kSettingsHaveBeenSetKey])
    [self syncPrefsFromInterface:nil];
  else
    [self syncInterfaceFromPrefs];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Private methods.

- (void)syncInterfaceFromPrefs {
  creditPushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushCreditKey];
  likePushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushLikeKey];
  favoritePushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushFavoriteKey];
  mentionPushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushMentionKey];
  commentPushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushCommentKey];
  replyPushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushReplyKey];
  followPushSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kPushFollowKey];
}

#pragma mark - Actions

- (IBAction)syncPrefsFromInterface:(id)sender {
  [[NSUserDefaults standardUserDefaults] setBool:[creditPushSwitch_ isOn]
                                          forKey:kPushCreditKey];
  [[NSUserDefaults standardUserDefaults] setBool:[likePushSwitch_ isOn]
                                          forKey:kPushLikeKey];
  [[NSUserDefaults standardUserDefaults] setBool:[favoritePushSwitch_ isOn]
                                          forKey:kPushFavoriteKey];
  [[NSUserDefaults standardUserDefaults] setBool:[mentionPushSwitch_ isOn]
                                          forKey:kPushMentionKey];
  [[NSUserDefaults standardUserDefaults] setBool:[commentPushSwitch_ isOn]
                                          forKey:kPushCommentKey];
  [[NSUserDefaults standardUserDefaults] setBool:[replyPushSwitch_ isOn]
                                          forKey:kPushReplyKey];
  [[NSUserDefaults standardUserDefaults] setBool:[followPushSwitch_ isOn]
                                          forKey:kPushFollowKey];
}

- (IBAction)settingsButtomPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
