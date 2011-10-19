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

@class UserImageView;
@class Stamp;
@class StampDetailAddCommentView;

@interface StampDetailViewController : UIViewController <UITextFieldDelegate,
                                                         RKObjectLoaderDelegate,
                                                         UIScrollViewDelegate,
                                                         TTTAttributedLabelDelegate> {
 @private
  Stamp* stamp_;
  // Managed by the view system.
  CAGradientLayer* activityGradientLayer_;
  // Preloaded Entity View.
  UIViewController* detailViewController_;
}

- (id)initWithStamp:(Stamp*)stamp;
- (IBAction)handleRestampButtonTap:(id)sender;
- (IBAction)handleTodoButtonTap:(id)sender;
- (IBAction)handleSendButtonTap:(id)sender;
- (IBAction)handleLikeButtonTap:(id)sender;
- (IBAction)handleEntityTap:(id)sender;

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
@property (nonatomic, retain) IBOutlet StampDetailAddCommentView* addCommentContainerView;

@end
