//
//  InboxViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@interface InboxViewController : STReloadableTableViewController <UIScrollViewDelegate, RKObjectLoaderDelegate> {
 @private
  BOOL userDidScroll_;
  
  IBOutlet UIView* filterView_;
  IBOutlet UIButton* placesFilterButton_;
  IBOutlet UIButton* booksFilterButton_;
  IBOutlet UIButton* filmsFilterButton_;
  IBOutlet UIButton* musicFilterButton_;
}

- (IBAction)filterButtonPushed:(id)sender;

@end
