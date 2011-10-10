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

typedef enum {
  SearchIntentStamp,
  SearchIntentTodo
} SearchIntent;


@interface SearchEntitiesViewController : UITableViewController <RKObjectLoaderDelegate,
                                                                 RKRequestDelegate,
                                                                 UITextFieldDelegate>

@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;
@property (nonatomic, retain) IBOutlet UITableViewCell* addStampCell;
@property (nonatomic, retain) IBOutlet UILabel* addStampLabel;
@property (nonatomic, retain) IBOutlet UITableViewCell* searchingIndicatorCell;
@property (nonatomic, retain) IBOutlet UILabel* fullSearchCellLabel;
@property (nonatomic, retain) IBOutlet UILabel* loadingIndicatorLabel;
@property (nonatomic, retain) IBOutlet UITableViewCell* fullSearchCell;
@property NSInteger searchIntent;

- (IBAction)cancelButtonTapped:(id)sender;
- (void)clearSearchField;

@end
