//
//  STCreateStampViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STCreditPickerController.h"
#import "STViewController.h"
#import "StampDetailHeaderView.h"
#import "ASIHTTPRequestDelegate.h"
#import "STUser.h"
#import "STEntity.h"

@class Entity;
@class UserImageView;
@class CAGradientLayer;
@class User;
@class SearchResult;

@interface STCreateStampViewController : STViewController <UITextViewDelegate,
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
@property (nonatomic, retain) id<STEntity> entityObject;
@property (nonatomic, retain) id<STUser> creditedUser;

@property (nonatomic, retain) IBOutlet UINavigationController* editEntityNavigationController;
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

- (id)initWithEntityObject:(id<STEntity>)entity;
- (id)initWithEntity:(id<STEntity>)entity creditedTo:(id<STUser>)user;

@end
