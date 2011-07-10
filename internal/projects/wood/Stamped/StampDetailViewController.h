//
//  StampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class StampEntity;

@interface StampDetailViewController : UIViewController {
 @private
  StampEntity* entity_;
}

- (id)initWithEntity:(StampEntity*)entity;

@property (nonatomic, retain) IBOutlet UITableViewCell* topHeaderCell;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UITextField* addCommentField;
@property (nonatomic, retain) IBOutlet UIView* commentsView;
@property (nonatomic, retain) IBOutlet UIView* activityView;
@property (nonatomic, retain) IBOutlet UIView* bottomToolbar;

@end
