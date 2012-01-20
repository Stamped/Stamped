//
//  CreateStampViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STCreditPickerController.h"
#import "STViewController.h"
#import "StampDetailHeaderView.h"
#import "ASIHTTPRequestDelegate.h"

@class Entity;
@class UserImageView;
@class CAGradientLayer;
@class User;
@class SearchResult;

@interface CreateStampViewController : STViewController <UITextViewDelegate,
                                                         RKObjectLoaderDelegate,
                                                         RKRequestDelegate,
                                                         STCreditPickerControllerDelegate,
                                                         UINavigationControllerDelegate,
                                                         UIImagePickerControllerDelegate,
                                                         UIActionSheetDelegate,
                                                         StampDetailHeaderViewDelegate,
                                                         ASIHTTPRequestDelegate> {
 @private
  CAGradientLayer* ribbonGradientLayer_;
  CALayer* stampLayer_;
}

@property (nonatomic, assign) BOOL newEntity;
@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) User* creditedUser;

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet StampDetailHeaderView* headerView;
@property (nonatomic, retain) IBOutlet UILabel* reasoningLabel;
@property (nonatomic, retain) IBOutlet UITextView* reasoningTextView;
@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIView* ribbonedContainerView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* spinner;
@property (nonatomic, retain) IBOutlet UIButton* stampItButton;
@property (nonatomic, retain) IBOutlet STCreditTextField* creditTextField;
@property (nonatomic, retain) IBOutlet UIButton* editButton;
@property (nonatomic, retain) IBOutlet UIView* mainCommentContainer;
@property (nonatomic, retain) IBOutlet UIImageView* backgroundImageView;
@property (nonatomic, retain) IBOutlet UIButton* tweetButton;
@property (nonatomic, retain) IBOutlet UIButton* fbButton;
@property (nonatomic, retain) IBOutlet UILabel* shareLabel;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* signInTwitterActivityIndicator;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* signInFacebookActivityIndicator;

- (IBAction)tweetButtonPressed:(id)sender;
- (IBAction)fbButtonPressed:(id)sender;
- (IBAction)editButtonPressed:(id)sender;
- (IBAction)saveStampButtonPressed:(id)sender;
- (id)initWithEntityObject:(Entity*)entityObject;
- (id)initWithSearchResult:(SearchResult*)searchResult;
- (id)initWithEntityObject:(Entity*)entityObject creditedTo:(User*)user;

@end
