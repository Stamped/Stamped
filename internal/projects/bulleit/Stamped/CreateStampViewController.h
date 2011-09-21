//
//  CreateStampViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@class Entity;
@class UserImageView;
@class CAGradientLayer;
@class User;
@class SearchResult;
@class STCreditTextField;

@interface CreateStampViewController : UIViewController<UITextFieldDelegate,
                                                        UITextViewDelegate,
                                                        RKObjectLoaderDelegate,
                                                        RKRequestDelegate,
                                                        UINavigationControllerDelegate,
                                                        UIImagePickerControllerDelegate,
                                                        UIActionSheetDelegate> {
 @private
  CAGradientLayer* ribbonGradientLayer_;
  CALayer* stampLayer_;
}

@property (nonatomic, assign) BOOL newEntity;
@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) User* creditedUser;

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* detailLabel;
@property (nonatomic, retain) IBOutlet UILabel* reasoningLabel;
@property (nonatomic, retain) IBOutlet UITextView* reasoningTextView;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIView* ribbonedContainerView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;
@property (nonatomic, retain) IBOutlet UIImageView* shelfBackground;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* spinner;
@property (nonatomic, retain) IBOutlet UIButton* stampItButton;
@property (nonatomic, retain) IBOutlet STCreditTextField* creditTextField;
@property (nonatomic, retain) IBOutlet UIButton* editButton;
@property (nonatomic, retain) IBOutlet UIView* mainCommentContainer;
@property (nonatomic, retain) IBOutlet UIImageView* backgroundImageView;
@property (nonatomic, retain) IBOutlet UILabel* creditLabel;
@property (nonatomic, retain) IBOutlet UIButton* tweetButton;
@property (nonatomic, retain) IBOutlet UILabel* shareLabel;

- (IBAction)tweetButtonPressed:(id)sender;
- (IBAction)editButtonPressed:(id)sender;
- (IBAction)backButtonPressed:(id)sender;
- (IBAction)saveStampButtonPressed:(id)sender;
- (id)initWithEntityObject:(Entity*)entityObject;
- (id)initWithSearchResult:(SearchResult*)searchResult;
- (id)initWithEntityObject:(Entity*)entityObject creditedTo:(User*)user;

@end
