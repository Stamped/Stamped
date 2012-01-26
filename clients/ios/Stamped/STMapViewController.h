//
//  STMapViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>
#import <UIKit/UIKit.h>

@class STSearchField;

@interface STMapViewController : UIViewController <MKMapViewDelegate>

@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;

- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)locationButtonPressed:(id)sender;

@end
