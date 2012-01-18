//
//  EditEntityViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "STCategoryDropdownTableView.h"

@class DetailedEntity;
@class STNavigationBar;

@interface EditEntityViewController : UIViewController <UITableViewDelegate, UITextFieldDelegate> {
 @private
  STEditCategoryRow selectedCategory_;
  UITextField* selectedTextField_;
}

@property (nonatomic, retain) IBOutlet STNavigationBar* navBar;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UITableView* categoryDropdownTableView;
@property (nonatomic, retain) IBOutlet UIImageView* menuArrow;
@property (nonatomic, retain) IBOutlet UIButton* categoryDropdownButton;
@property (nonatomic, retain) IBOutlet UIImageView* categoryDropdownImageView;
@property (nonatomic, retain) IBOutlet UITextField* entityNameTextField;
@property (nonatomic, retain) IBOutlet UITextField* primaryTextField;
@property (nonatomic, retain) IBOutlet UITextField* secondaryTextField;
@property (nonatomic, retain) IBOutlet UITextField* tertiaryTextField;
@property (nonatomic, retain) IBOutlet UITextField* descriptionTextField;
@property (nonatomic, retain) IBOutlet UIButton* addLocationButton;
@property (nonatomic, retain) IBOutlet UIButton* addDescriptionButton;
@property (nonatomic, retain) IBOutlet UIView* addLocationView;
@property (nonatomic, retain) IBOutlet UITextField* streetTextField;
@property (nonatomic, retain) IBOutlet UITextField* secondStreetTextField;
@property (nonatomic, retain) IBOutlet UITextField* cityTextField;
@property (nonatomic, retain) IBOutlet UITextField* stateTextField;
@property (nonatomic, retain) IBOutlet UITextField* zipTextField;

@property (nonatomic, retain) UISegmentedControl* segmentedControl;

- (id)initWithDetailedEntity:(DetailedEntity*)detailedEntity;

@property (nonatomic, retain) DetailedEntity* detailedEntity;

- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)doneButtonPressed:(id)sender;
- (IBAction)addDescriptionButtonPressed:(id)sender;
- (IBAction)categoryDropdownPressed:(id)sender;
- (IBAction)addLocationButtonPressed:(id)sender;
@end