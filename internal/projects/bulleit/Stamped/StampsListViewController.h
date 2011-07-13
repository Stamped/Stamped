//
//  StampsListViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface StampsListViewController : UITableViewController<UIScrollViewDelegate> {
 @private
  BOOL userDidScroll_;
  NSArray* filterButtons_;
  NSMutableArray* stampsArray_;
  
  IBOutlet UIView* filterView_;
  IBOutlet UIButton* placesFilterButton_;
  IBOutlet UIButton* booksFilterButton_;
  IBOutlet UIButton* filmsFilterButton_;
  IBOutlet UIButton* musicFilterButton_;
}

- (IBAction)filterButtonPushed:(id)sender;

@end
