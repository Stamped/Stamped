//
//  CollapsibleViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CollapsibleViewController;

@protocol CollapsibleViewControllerDelegate
@required
- (void)collapsibleViewController:(CollapsibleViewController*)collapsibleVC willChangeHeightBy:(CGFloat)delta;
- (UIImageView*)imageView;
@end

@interface CollapsibleViewController : UIViewController {
 @protected
  BOOL isCollapsed;
  BOOL previewMode;
  NSMutableDictionary* contentDict;
  CGFloat maxNameLabelWidth;
  CGFloat collapsedHeight;
  NSString* collapsedFooterText;
  NSString* expandedFooterText;
  
  NSMutableArray* stamps;
}

- (void)setIsCollapsed:(BOOL)collapsed;
- (void)collapse;
- (void)expand;
- (void)collapseAnimated;
- (void)expandAnimated;
- (void)swapArrowImage;
- (void)moveArrowViewIfOccluded;

- (void)addPairedLabelWithName:(NSString*)name value:(NSString*)value forKey:(NSString*)key;
- (void)addText:(NSString*)text forKey:(NSString*)key;
- (void)addWrappingText:(NSString*)text forKey:(NSString*)key;
- (void)addNumberedListWithValues:(NSArray*)values;
- (void)addImagesForStamps:(NSSet*)stamps;
- (void)addContent:(id)content forKey:(NSString*)key;
- (float)contentHeight;

@property (nonatomic, retain) IBOutlet UIView* headerView;
@property (nonatomic, retain) IBOutlet UIView* footerView;
@property (nonatomic, retain) IBOutlet UIView* contentView;
@property (nonatomic, retain) IBOutlet UIImageView* arrowView;
@property (nonatomic, retain) IBOutlet UIImageView* iconView;
@property (nonatomic, retain) IBOutlet UILabel* sectionLabel;
@property (nonatomic, retain) IBOutlet UILabel* numLabel;
@property (nonatomic, retain) IBOutlet UILabel* footerLabel;

@property (nonatomic, assign) UIImageView* imageView;
@property (nonatomic, retain) NSString* collapsedFooterText;
@property (nonatomic, retain) NSString* expandedFooterText;
@property (nonatomic, retain) NSMutableDictionary* contentDict;
@property (nonatomic, assign) BOOL isCollapsed;
@property (nonatomic, assign) CGFloat collapsedHeight;
@property (nonatomic, retain) NSArray* stamps;

@property (nonatomic, assign) id<CollapsibleViewControllerDelegate> delegate;

extern int const COLLAPSED_HEIGHT;
extern int const LABEL_HEIGHT;
extern int const IMAGE_HEIGHT;
extern int const SPACE_HEIGHT;


@end

