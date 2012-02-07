//
//  SearchEntitiesViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STStampFilterBar.h"

@class STSearchField;

typedef enum {
  SearchIntentStamp,
  SearchIntentTodo
} SearchIntent;

@interface SearchEntitiesViewController : UIViewController <RKObjectLoaderDelegate,
                                                            RKRequestDelegate,
                                                            STStampFilterBarDelegate,
                                                            UITextFieldDelegate,
                                                            UITableViewDelegate,
                                                            UITableViewDataSource>

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet UIImageView* nearbyImageView;
@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* locationButton;
@property (nonatomic, retain) IBOutlet UITableViewCell* addStampCell;
@property (nonatomic, retain) IBOutlet UILabel* addStampLabel;
@property (nonatomic, retain) IBOutlet UITableViewCell* searchingIndicatorCell;
@property (nonatomic, retain) IBOutlet UILabel* loadingIndicatorLabel;
@property (nonatomic, retain) IBOutlet UIButton* searchButton;

@property (nonatomic, assign) SearchIntent searchIntent;

- (IBAction)locationButtonPressed:(id)sender;
- (IBAction)searchButtonPressed:(id)sender;
- (IBAction)cancelButtonPressed:(id)sender;
- (void)resetState;

@end
