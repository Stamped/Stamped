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

@class MKMapView;

@interface InboxViewController : STReloadableTableViewController <UIScrollViewDelegate, RKObjectLoaderDelegate> {
 @private
  BOOL userDidScroll_;
}

@property (nonatomic, readonly) MKMapView* mapView;
@property (nonatomic, assign) IBOutlet UIView* filterView;
@property (nonatomic, retain) IBOutlet UIButton* foodFilterButton;
@property (nonatomic, retain) IBOutlet UIButton* booksFilterButton;
@property (nonatomic, retain) IBOutlet UIButton* filmFilterButton;
@property (nonatomic, retain) IBOutlet UIButton* musicFilterButton;
@property (nonatomic, retain) IBOutlet UIButton* otherFilterButton;

- (IBAction)filterButtonPushed:(id)sender;

@end
