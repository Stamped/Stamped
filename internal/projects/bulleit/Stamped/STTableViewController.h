//
//  STTableViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STTableViewController : UIViewController <UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet UIView* shelfView;

@property (nonatomic, assign) BOOL shouldReload;
@property (nonatomic, assign) BOOL hasHeaders;
@property (nonatomic, assign) BOOL hasFilterBar;
@property (nonatomic, assign) BOOL isLoading;
@property (nonatomic, readonly) UILabel* reloadLabel;
@property (nonatomic, readonly) UILabel* lastUpdatedLabel;
@property (nonatomic, readonly) UIImageView* arrowImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* spinnerView;

- (void)userPulledToReload;
- (void)reloadData;
- (void)updateLastUpdatedTo:(NSDate*)date;

@end
