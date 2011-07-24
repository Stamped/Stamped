//
//  CreateStampViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface CreateStampViewController : UITableViewController<UITextInputDelegate>

@property (nonatomic, retain) IBOutlet UITextField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;

- (IBAction)cancelButtonTapped:(id)sender;

@end
