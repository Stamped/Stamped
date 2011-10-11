//
//  InboxViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"
#import "STStampFilterBar.h"

@interface InboxViewController : STReloadableTableViewController <UIScrollViewDelegate,
                                                                  RKObjectLoaderDelegate,
                                                                  MKMapViewDelegate,
                                                                  STStampFilterBarDelegate>
@property (nonatomic, readonly) MKMapView* mapView;
@property (nonatomic, retain) IBOutlet STStampFilterBar* stampFilterBar;
@end
