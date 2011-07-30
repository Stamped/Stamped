//
//  CreateStampViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@interface CreateStampViewController : UITableViewController <RKObjectLoaderDelegate, UITextFieldDelegate>

@property (nonatomic, retain) IBOutlet UITextField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;

- (IBAction)cancelButtonTapped:(id)sender;

@end
