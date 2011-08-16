//
//  PlaceDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <MapKit/MapKit.h>

@class STPlaceAnnotation;

@interface PlaceDetailViewController : EntityDetailViewController <MKMapViewDelegate> {
 @private
  STPlaceAnnotation* annotation_;
  CLLocationDegrees latitude_;
  CLLocationDegrees longitude_;
}

- (IBAction)reservationButtonPressed:(id)sender;
- (IBAction)callButtonPressed:(id)sender;

@property (nonatomic, retain) IBOutlet UIView* mainContentView;
@property (nonatomic, retain) IBOutlet UIButton* callActionButton;
@property (nonatomic, retain) IBOutlet UILabel* callActionLabel;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;

@end
