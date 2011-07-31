//
//  PlaceDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <MapKit/MapKit.h>

@interface PlaceDetailViewController : EntityDetailViewController <MKMapViewDelegate>

- (IBAction)reservationButtonPressed:(id)sender;
- (IBAction)callButtonPressed:(id)sender;

@property (nonatomic, retain) IBOutlet UIView* mainActionsView;
@property (nonatomic, retain) IBOutlet UIView* mainContentView;
@property (nonatomic, retain) IBOutlet UIButton* callActionButton;
@property (nonatomic, retain) IBOutlet UILabel* callActionLabel;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;

@property (nonatomic, assign) BOOL hidesMainActions;

@end
