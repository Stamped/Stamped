//
//  EditEntityViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Entity;

@interface EditEntityViewController : UIViewController <UITableViewDelegate>

@property (nonatomic, retain) IBOutlet UITableView* categoryDropdownTableView;
@property (nonatomic, retain) IBOutlet UIButton* categoryDropdownButton;
@property (nonatomic, retain) IBOutlet UIImageView* categoryDropdownImageView;
@property (nonatomic, retain) IBOutlet UITextField* entityNameTextField;
@property (nonatomic, retain) IBOutlet UITextField* categoryTextField;
@property (nonatomic, retain) IBOutlet UIButton* addLocationButton;
@property (nonatomic, retain) IBOutlet UIButton* addDescriptionButton;
@property (nonatomic, retain) IBOutlet UIView* addLocationView;


- (id)initWithEntity:(Entity*)entityObject;

@property (nonatomic, retain) Entity* entityObject;

- (IBAction)categoryDropdownPressed:(id)sender;
- (IBAction)addLocationButtonPressed:(id)sender;
@end
