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

@interface OtherDetailViewController : EntityDetailViewController <MKMapViewDelegate> {
 @private
  STPlaceAnnotation* annotation_;
  CLLocationDegrees latitude_;
  CLLocationDegrees longitude_;
}

- (IBAction)callButtonPressed:(id)sender;

@property (nonatomic, retain) IBOutlet UIButton* callActionButton;
@property (nonatomic, retain) IBOutlet UILabel* callActionLabel;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;
@property (nonatomic, retain) IBOutlet UIView* mapContainerView;
@property (nonatomic, retain) IBOutlet UIView* appActionsView;

@end
