//
//  SearchEntitiesViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@class STSearchField;

@interface SearchEntitiesViewController : UITableViewController <RKObjectLoaderDelegate,
                                                                 RKRequestDelegate,
                                                                 UITextFieldDelegate>

@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* locationButton;
@property (nonatomic, retain) IBOutlet UITableViewCell* addStampCell;
@property (nonatomic, retain) IBOutlet UILabel* addStampLabel;
@property (nonatomic, retain) IBOutlet UITableViewCell* searchingIndicatorCell;
@property (nonatomic, retain) IBOutlet UILabel* fullSearchCellLabel;
@property (nonatomic, retain) IBOutlet UILabel* loadingIndicatorLabel;
@property (nonatomic, retain) IBOutlet UITableViewCell* fullSearchCell;

- (IBAction)locationButtonTapped:(id)sender;
- (IBAction)cancelButtonTapped:(id)sender;
- (void)clearSearchField;

@end
