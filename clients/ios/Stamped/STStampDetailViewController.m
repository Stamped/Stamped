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
#import "CreateStampViewController.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "STStampDetailHeader.h"
#import "STStampDetailToolbar.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"

static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static NSString* const kCreateLikePath = @"/stamps/likes/create.json";
static NSString* const kRemoveLikePath = @"/stamps/likes/remove.json";

typedef enum {
  StampDetailActionTypeDeleteComment = 0,
  StampDetailActionTypeRetrySend,
  StampDetailActionTypeDeleteStamp,
  StampDetailActionTypeShare
} StampDetailActionType;

@interface STStampDetailViewController ()
@property (nonatomic, retain) Stamp* stamp;

- (void)_showEmailViewController;
- (void)_showTweetViewController;
- (void)_headerPressed:(id)sender;
- (void)_todoButtonPressed:(id)sender;
- (void)_likeButtonPressed:(id)sender;
- (void)_shareButtonPressed:(id)sender;
- (void)_restampButtonPressed:(id)sender;
@end

@implementation STStampDetailViewController

@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;
@synthesize header = _header;

- (id)initWithStamp:(Stamp*)stamp {
  self = [super initWithNibName:@"STStampDetailViewController" bundle:nil];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [_stamp release];
  self.toolbar = nil;
  self.header = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  if ([[AccountManager sharedManager].currentUser.screenName isEqualToString:_stamp.user.screenName])
    _toolbar.style = STStampDetailToolbarStyleMine;

  _toolbar.likeButton.selected = _stamp.isLiked.boolValue;
  [_toolbar.likeButton addTarget:self
                          action:@selector(_likeButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
  _toolbar.todoButton.selected = _stamp.entityObject.favorite != nil;
  [_toolbar.todoButton addTarget:self
                          action:@selector(_todoButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
  [_toolbar.shareButton addTarget:self
                           action:@selector(_shareButtonPressed:)
                 forControlEvents:UIControlEventTouchUpInside];
  [_toolbar.stampButton addTarget:self
                           action:@selector(_restampButtonPressed:)
                 forControlEvents:UIControlEventTouchUpInside];
  
  _header.subtitleLabel.text = _stamp.entityObject.subtitle;
  _header.categoryImageView.image = _stamp.entityObject.stampDetailCategoryImage;
  _header.stampImage = [_stamp.user stampImageWithSize:StampImageSize46];
  _header.title = _stamp.entityObject.title;
  [_header addTarget:self action:@selector(_headerPressed:) forControlEvents:UIControlEventTouchUpInside];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.toolbar = nil;
  self.header = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (actionSheet.tag == StampDetailActionTypeShare) {
    BOOL canTweet = NO;
    if ([TWTweetComposeViewController canSendTweet] &&
        [AccountManager.sharedManager.currentUser.screenName isEqualToString:_stamp.user.screenName]) {
      canTweet = YES;
    }
    if ([[actionSheet buttonTitleAtIndex:buttonIndex] isEqualToString:NSLocalizedString(@"Copy link", nil)]) {  // Copy link...
      [UIPasteboard generalPasteboard].string = _stamp.URL;
    } else if ([[actionSheet buttonTitleAtIndex:buttonIndex] isEqualToString:NSLocalizedString(@"Share to Twitter", nil)] && canTweet) {  // Twitter or cancel depending...
      [self _showTweetViewController];
    } else if ([[actionSheet buttonTitleAtIndex:buttonIndex] isEqualToString:NSLocalizedString(@"Email stamp", nil)]) {
      [self _showEmailViewController];
    }
  }
}

#pragma mark - MFMailComposeViewControllerDelegate methods.

- (void)mailComposeController:(MFMailComposeViewController*)controller 
          didFinishWithResult:(MFMailComposeResult)result
                        error:(NSError*)error {
  [self dismissModalViewControllerAnimated:YES];
}

#pragma mark - Private methods.

- (void)_showEmailViewController {
  MFMailComposeViewController* vc = [[MFMailComposeViewController alloc] init];
  vc.mailComposeDelegate = self;
  [vc setSubject:[NSString stringWithFormat:NSLocalizedString(@"Check out this stamp of %@", nil), _stamp.entityObject.title]];
  [vc setMessageBody:[NSString stringWithFormat:NSLocalizedString(@"<a href=\"%@\">%@</a><br/><br/>(Sent via <a href=\"http://stamped.com/\">Stamped</a>)", nil), _stamp.URL, _stamp.URL]
              isHTML:YES];
  [self presentModalViewController:vc animated:YES];
  [vc release];
}

- (void)_showTweetViewController {
  TWTweetComposeViewController* twitter = [[[TWTweetComposeViewController alloc] init] autorelease];
  NSString* blurb = [NSString stringWithFormat:NSLocalizedString(@"%@. \u201c%@\u201d", nil), _stamp.entityObject.title, _stamp.blurb];
  if (_stamp.blurb.length == 0)
    blurb = [_stamp.entityObject.title stringByAppendingString:@"."];
  
  BOOL hasImage = _stamp.imageURL != nil;
  
  NSString* substring = [blurb substringToIndex:MIN(blurb.length, hasImage ? 98 : 104)];
  if (blurb.length > substring.length)
    blurb = [substring stringByAppendingString:@"..."];
  
  NSString* initial = hasImage ? NSLocalizedString(@"Stamped [pic]:", nil) : NSLocalizedString(@"Stamped:", nil);
  // Stamped ([pic]): [blurb] [link]
  [twitter setInitialText:[NSString stringWithFormat:@"%@ %@ %@", initial, blurb, _stamp.URL]];
  
  if ([TWTweetComposeViewController canSendTweet]) {
    [self presentViewController:twitter animated:YES completion:nil];
  }
  
  twitter.completionHandler = ^(TWTweetComposeViewControllerResult result) {
    [self dismissModalViewControllerAnimated:YES];
  };
}

- (void)_headerPressed:(id)sender {
  EntityDetailViewController* vc = (EntityDetailViewController*)[Util detailViewControllerForEntity:_stamp.entityObject];
  vc.referringStamp = _stamp;
  [self.navigationController pushViewController:vc animated:YES];
}

#pragma mark - Toolbar methods.

- (void)_todoButtonPressed:(id)sender {
  BOOL shouldRemove = _stamp.entityObject.favorite != nil;
  NSString* path = shouldRemove ? kRemoveFavoritePath : kCreateFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  if (shouldRemove) {
    objectLoader.params = [NSDictionary dictionaryWithObject:_stamp.entityObject.entityID forKey:@"entity_id"];
    _stamp.entityObject.favorite = nil;
    [Stamp.managedObjectContext save:NULL];
  } else {
    objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
                           _stamp.entityObject.entityID, @"entity_id",
                           _stamp.stampID, @"_stampid", nil];
  }
  [objectLoader send];
}

- (void)_likeButtonPressed:(id)sender {
  BOOL shouldRemove = _stamp.isLiked.boolValue;
  NSString* path = shouldRemove ? kRemoveLikePath : kCreateLikePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:_stamp.stampID, @"_stampid", nil];

  [objectLoader send];
}

- (void)_shareButtonPressed:(id)sender {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:nil
                                                      delegate:self
                                             cancelButtonTitle:nil
                                        destructiveButtonTitle:nil
                                             otherButtonTitles:nil] autorelease];
  
  if ([TWTweetComposeViewController canSendTweet] &&
      [AccountManager.sharedManager.currentUser.screenName isEqualToString:_stamp.user.screenName]) {
    [sheet addButtonWithTitle:NSLocalizedString(@"Share to Twitter", nil)];
  }
  
  if ([MFMailComposeViewController canSendMail])
    [sheet addButtonWithTitle:NSLocalizedString(@"Email stamp", nil)];
  
  [sheet addButtonWithTitle:NSLocalizedString(@"Copy link", nil)];
  sheet.cancelButtonIndex = [sheet addButtonWithTitle:NSLocalizedString(@"Cancel", nil)];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  sheet.tag = StampDetailActionTypeShare;
  [sheet showInView:self.view];
}

- (void)_restampButtonPressed:(id)sender {
  CreateStampViewController* vc = [[CreateStampViewController alloc] initWithEntityObject:_stamp.entityObject
                                                                               creditedTo:_stamp.user];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

@end
