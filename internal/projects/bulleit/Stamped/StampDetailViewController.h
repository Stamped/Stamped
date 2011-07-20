//
//  StampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class UserImageView;
@class Stamp;

@interface StampDetailViewController : UIViewController {
 @private
  Stamp* stamp_;
}

- (id)initWithStamp:(Stamp*)stamp;

@property (nonatomic, retain) IBOutlet UITableViewCell* topHeaderCell;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UITextField* addCommentField;
@property (nonatomic, retain) IBOutlet UIView* commentsView;
@property (nonatomic, retain) IBOutlet UIView* activityView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;
@property (nonatomic, retain) IBOutlet UserImageView* currentUserImageView;
@property (nonatomic, retain) IBOutlet UserImageView* commenterImageView;
@property (nonatomic, retain) IBOutlet UILabel* commenterNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* stampedLabel;


@end
