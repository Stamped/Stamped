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
#import "STImageView.h"
#import "ShowImageViewController.h"
#import "STViewController.h"
#import "Util.h"
#import "STEntityDetail.h"
#import "STViewDelegate.h"

@class Entity;
@class DetailedEntity;
@class SearchResult;
@class Stamp;
@class STToolbar;

extern BOOL const newEDetail;

@interface EntityDetailViewController : STViewController <RKObjectLoaderDelegate, 
                                                          CollapsibleViewControllerDelegate,
                                                          STImageViewDelegate,
                                                          STViewDelegate> {
 @protected
  DetailedEntity* detailedEntity_;
  Entity* entityObject_;
  SearchResult* searchResult_;
  BOOL viewIsVisible_;
  BOOL dataLoaded_;
  NSMutableDictionary* sectionsDict_;
}

- (IBAction)mainActionButtonPressed:(id)sender;
- (IBAction)todoButtonPressed:(id)sender;
- (IBAction)stampButtonPressed:(id)sender;

- (id)initWithEntityObject:(Entity*)entity;
- (id)initWithSearchResult:(SearchResult*)searchResult;
- (void)addSectionWithName:(NSString*)name;
- (void)addSectionWithName:(NSString*)name previewHeight:(CGFloat)previewHeight;
- (void)appendChildView:(UIView*)section;
- (void)addSectionStampedBy;
- (void)addTodoToolbar;
- (void)hideMainToolbar;
- (CGFloat)contentHeight;
- (CollapsibleViewController*)makeSectionWithName:(NSString*)name;
- (void)addSection:(CollapsibleViewController*)section;
- (NSUInteger)lineCountOfLabel:(UILabel*)label;
- (void)didLoadEntityDetail:(id<STEntityDetail>)anEntityDetail;

@property (nonatomic, retain) Stamp* referringStamp;
@property (nonatomic, readonly) id<STEntityDetail> entityDetail;
@property (nonatomic, readonly) NSMutableArray* detailComponents;
@property (nonatomic, readonly) NSOperationQueue* operationQueue;

@property (nonatomic, retain) IBOutlet STToolbar* toolbarView;
@property (nonatomic, retain) IBOutlet UIButton* todoButton;
@property (nonatomic, retain) IBOutlet UILabel* todoLabel;
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
@property (nonatomic, retain) IBOutlet STImageView* imageView;

- (void)imageViewTapped;

@end
