//
//  EntityDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>

@class Entity;

@interface EntityDetailViewController : UIViewController <RKObjectLoaderDelegate> {
 @protected
  Entity* entityObject_;
  BOOL viewIsVisible_;
  BOOL dataLoaded_;
}

- (id)initWithEntityObject:(Entity*)entity;

@property (nonatomic, retain) IBOutlet UIView* mainActionsView;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* descriptionLabel;
@property (nonatomic, retain) IBOutlet UIButton* mainActionButton;
@property (nonatomic, retain) IBOutlet UILabel* mainActionLabel;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingView;

@end
