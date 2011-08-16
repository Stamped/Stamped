//
//  SearchEntitiesViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <CoreLocation/CoreLocation.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@class STSearchField;

@interface SearchEntitiesViewController : UITableViewController <RKObjectLoaderDelegate,
                                                                 UITextFieldDelegate>

@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;

- (IBAction)cancelButtonTapped:(id)sender;

@end
