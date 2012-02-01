//
//  STTableViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "STStampFilterBar.h"
#import "STViewController.h"

@interface STTableViewController : STViewController <UIScrollViewDelegate,
                                                     UITextFieldDelegate,
                                                     STStampFilterBarDelegate>

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet STStampFilterBar* stampFilterBar;
@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;

@property (nonatomic, assign) BOOL disableReload;
@property (nonatomic, assign) BOOL shouldReload;
@property (nonatomic, assign) BOOL hasHeaders;
@property (nonatomic, assign) BOOL isLoading;
@property (nonatomic, readonly) UILabel* reloadLabel;
@property (nonatomic, readonly) UILabel* lastUpdatedLabel;
@property (nonatomic, readonly) UIImageView* arrowImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* spinnerView;
@property (nonatomic, retain) UIView* searchOverlay;

- (IBAction)cancelButtonPressed:(id)sender;
- (void)userPulledToReload;
- (void)reloadData;
- (void)updateLastUpdatedTo:(NSDate*)date;

@end
