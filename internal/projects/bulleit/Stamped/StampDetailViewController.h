//
//  StampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <QuartzCore/QuartzCore.h>
#import <UIKit/UIKit.h>

#import "TTTAttributedLabel.h"
#import "StampDetailCommentView.h"

extern NSString* const kRemoveCommentPath;
extern NSString* const kRemoveStampPath;

@class UserImageView;
@class Stamp;

@interface StampDetailViewController : UIViewController <UITextFieldDelegate,
                                                         UIActionSheetDelegate,
                                                         UIScrollViewDelegate,
                                                         RKObjectLoaderDelegate,
                                                         TTTAttributedLabelDelegate,
                                                         StampDetailCommentViewDelegate> {
 @private
  Stamp* stamp_;
  // Managed by the view system.
  CAGradientLayer* activityGradientLayer_;
}

- (id)initWithStamp:(Stamp*)stamp;
- (IBAction)handleRestampButtonTap:(id)sender;
- (IBAction)handleTodoButtonTap:(id)sender;
- (IBAction)handleShareButtonTap:(id)sender;
- (IBAction)handleLikeButtonTap:(id)sender;
- (IBAction)handleEntityTap:(id)sender;
- (IBAction)sendButtonPressed:(id)sender;

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIView* mainCommentContainer;
@property (nonatomic, retain) IBOutlet UIView* commentsView;
@property (nonatomic, retain) IBOutlet UIView* activityView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;
@property (nonatomic, retain) IBOutlet UserImageView* commenterImageView;
@property (nonatomic, retain) IBOutlet UILabel* commenterNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* stampedLabel;
@property (nonatomic, retain) IBOutlet UIButton* addFavoriteButton;
@property (nonatomic, retain) IBOutlet UILabel* addFavoriteLabel;
@property (nonatomic, retain) IBOutlet UIButton* likeButton;
@property (nonatomic, retain) IBOutlet UILabel* likeLabel;
@property (nonatomic, retain) IBOutlet UIButton* shareButton;
@property (nonatomic, retain) IBOutlet UILabel* shareLabel;
@property (nonatomic, retain) IBOutlet UIButton* stampButton;
@property (nonatomic, retain) IBOutlet UILabel* stampLabel;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* subtitleLabel;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UILabel* timestampLabel;
@property (nonatomic, retain) IBOutlet UserImageView* currentUserImageView;
@property (nonatomic, retain) IBOutlet UITextField* commentTextField;
@property (nonatomic, retain) IBOutlet UIButton* sendButton;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* sendIndicator;
@property (nonatomic, retain) IBOutlet UIView* alsoStampedByContainer;
@property (nonatomic, retain) IBOutlet UILabel* alsoStampedByLabel;
@property (nonatomic, retain) IBOutlet UIScrollView* alsoStampedByScrollView;



@end
