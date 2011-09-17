//
//  EntityDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import "CollapsibleViewController.h"
#import "UIColor+Stamped.h"

@class Entity;

@interface EntityDetailViewController : UIViewController <RKObjectLoaderDelegate, CollapsibleViewControllerDelegate> {
 @protected
  Entity* entityObject_;
  BOOL viewIsVisible_;
  BOOL dataLoaded_;
  NSMutableDictionary* sectionsDict_;
}

- (id)initWithEntityObject:(Entity*)entity;
- (void)addSectionWithName:(NSString*)name;
- (void)addSectionWithName:(NSString*)name previewHeight:(CGFloat)previewHeight;
- (void)addSectionStampedBy;
- (CGFloat)contentHeight;

@property (nonatomic, retain) IBOutlet UIView* mainActionsView;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* descriptionLabel;
@property (nonatomic, retain) IBOutlet UIButton* mainActionButton;
@property (nonatomic, retain) IBOutlet UILabel* mainActionLabel;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingView;
@property (nonatomic, retain) IBOutlet UIView* mainContentView;


@end
