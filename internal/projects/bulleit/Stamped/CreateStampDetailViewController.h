//
//  CreateStampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Entity;
@class STNavigationBar;
@class UserImageView;

@interface CreateStampDetailViewController : UIViewController<UITextViewDelegate> {
 @private
  Entity* entityObject_;
}

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* detailLabel;
@property (nonatomic, retain) IBOutlet UILabel* reasoningLabel;
@property (nonatomic, retain) IBOutlet UITextView* reasoningTextView;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet STNavigationBar* navigationBar;
@property (nonatomic, retain) IBOutlet UIView* ribbonedContainerView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;

- (IBAction)reasoningTextPressed:(id)sender;
- (IBAction)backOrCancelButtonPressed:(id)sender;
- (id)initWithEntityObject:(Entity*)entityObject;

@end
