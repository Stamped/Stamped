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

@synthesize creditEmailSwitch = creditEmailSwitch_;
@synthesize likeEmailSwitch = likeEmailSwitch_;
@synthesize favoriteEmailSwitch = favoriteEmailSwitch_;
@synthesize mentionEmailSwitch = mentionEmailSwitch_;
@synthesize commentEmailSwitch = commentEmailSwitch_;
@synthesize replyEmailSwitch = replyEmailSwitch_;
@synthesize followEmailSwitch = followEmailSwitch_;

- (id)init {
  self = [self initWithNibName:@"NotificationSettingsViewController" bundle:nil];
  if (self) {}
  return self;
}

- (void)dealloc {
  self.scrollView = nil;

  self.creditPushSwitch = nil;
  self.likePushSwitch = nil;
  self.favoritePushSwitch = nil;
  self.mentionPushSwitch = nil;
  self.commentPushSwitch = nil;
  self.replyPushSwitch = nil;
  self.followPushSwitch = nil;

  self.creditEmailSwitch = nil;
  self.likeEmailSwitch = nil;
  self.favoriteEmailSwitch = nil;
  self.mentionEmailSwitch = nil;
  self.commentEmailSwitch = nil;
  self.replyEmailSwitch = nil;
  self.followEmailSwitch = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  scrollView_.contentSize = CGSizeMake(320, 790);
  if (![[NSUserDefaults standardUserDefaults] boolForKey:kSettingsHaveBeenSetKey]) {
    [self syncPrefsFromInterface:nil];
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:kSettingsHaveBeenSetKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
  } else {
    [self syncInterfaceFromPrefs];
  }
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;

  self.creditPushSwitch = nil;
  self.likePushSwitch = nil;
  self.favoritePushSwitch = nil;
  self.mentionPushSwitch = nil;
  self.commentPushSwitch = nil;
  self.replyPushSwitch = nil;
  self.followPushSwitch = nil;

  self.creditEmailSwitch = nil;
  self.likeEmailSwitch = nil;
  self.favoriteEmailSwitch = nil;
  self.mentionEmailSwitch = nil;
  self.commentEmailSwitch = nil;
  self.replyEmailSwitch = nil;
  self.followEmailSwitch = nil;
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

  creditEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailCreditKey];
  likeEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailLikeKey];
  favoriteEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailFavoriteKey];
  mentionEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailMentionKey];
  commentEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailCommentKey];
  replyEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailReplyKey];
  followEmailSwitch_.on = [[NSUserDefaults standardUserDefaults] boolForKey:kEmailFollowKey];
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

  [[NSUserDefaults standardUserDefaults] setBool:[creditEmailSwitch_ isOn]
                                          forKey:kEmailCreditKey];
  [[NSUserDefaults standardUserDefaults] setBool:[likeEmailSwitch_ isOn]
                                          forKey:kEmailLikeKey];
  [[NSUserDefaults standardUserDefaults] setBool:[favoriteEmailSwitch_ isOn]
                                          forKey:kEmailFavoriteKey];
  [[NSUserDefaults standardUserDefaults] setBool:[mentionEmailSwitch_ isOn]
                                          forKey:kEmailMentionKey];
  [[NSUserDefaults standardUserDefaults] setBool:[commentEmailSwitch_ isOn]
                                          forKey:kEmailCommentKey];
  [[NSUserDefaults standardUserDefaults] setBool:[replyEmailSwitch_ isOn]
                                          forKey:kEmailReplyKey];
  [[NSUserDefaults standardUserDefaults] setBool:[followEmailSwitch_ isOn]
                                          forKey:kEmailFollowKey];

  [[NSUserDefaults standardUserDefaults] synchronize];
}

- (IBAction)settingsButtomPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
