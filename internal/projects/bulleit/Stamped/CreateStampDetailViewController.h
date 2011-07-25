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

@interface CreateStampDetailViewController : UIViewController {
 @private
  Entity* entityObject_;
}

@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* detailLabel;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet STNavigationBar* navigationBar;

- (IBAction)backButtonPressed:(id)sender;
- (id)initWithEntity:(Entity*)entityObject;

@end
