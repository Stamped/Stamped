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
@class DetailedEntity;
@class SearchResult;
@class Stamp;

@interface EntityDetailViewController : UIViewController <RKObjectLoaderDelegate, CollapsibleViewControllerDelegate> {
 @protected
  DetailedEntity* detailedEntity_;
  Entity* entityObject_;
  SearchResult* searchResult_;
  BOOL viewIsVisible_;
  BOOL dataLoaded_;
  NSMutableDictionary* sectionsDict_;
}

- (id)initWithEntityObject:(Entity*)entity;
- (id)initWithSearchResult:(SearchResult*)searchResult;
- (void)addSectionWithName:(NSString*)name;
- (void)addSectionWithName:(NSString*)name previewHeight:(CGFloat)previewHeight;
- (void)addSectionStampedBy;
- (void)addToolbar;
- (CGFloat)contentHeight;
- (CollapsibleViewController*)makeSectionWithName:(NSString*)name;
- (void)addSection:(CollapsibleViewController*)section;
- (NSUInteger)lineCountOfLabel:(UILabel*)label;

@property (nonatomic, retain) IBOutlet UIView* mainActionsView;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* descriptionLabel;
@property (nonatomic, retain) IBOutlet UIButton* mainActionButton;
@property (nonatomic, retain) IBOutlet UILabel* mainActionLabel;
@property (nonatomic, retain) IBOutlet UIImageView* categoryImageView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingView;
@property (nonatomic, retain) IBOutlet UIView* mainContentView;
@property (nonatomic, retain) IBOutlet UIImageView* shelfImageView;


@end
