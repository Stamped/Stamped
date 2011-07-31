//
//  PlaceDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "PlaceDetailViewController.h"

#import <CoreLocation/CoreLocation.h>
#import <QuartzCore/QuartzCore.h>

@interface PlaceAnnotation : NSObject<MKAnnotation> {
 @private
  CLLocationDegrees latitude_;
  CLLocationDegrees longitude_;
}

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude;

@end

@implementation PlaceAnnotation

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude {
  self = [super init];
  if (self) {
    latitude_ = latitude;
    longitude_ = longitude;
  }
  return self;
}

- (CLLocationCoordinate2D)coordinate {
  return CLLocationCoordinate2DMake(latitude_, longitude_); 
}

@end

@interface PlaceDetailViewController ()
- (void)confirmCall;
@end

@implementation PlaceDetailViewController

@synthesize mainActionsView = mainActionsView_;
@synthesize mainContentView = mainContentView_;
@synthesize callActionButton = callActionButton_;
@synthesize callActionLabel = callActionLabel_;
@synthesize mapView = mapView_;
@synthesize hidesMainActions = hidesMainActions_;  // Scalar.

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  hidesMainActions_ = YES;
  if (hidesMainActions_) {
    mainContentView_.frame = CGRectOffset(mainContentView_.frame, 0, -CGRectGetHeight(mainActionsView_.frame));
    self.mainActionsView.hidden = YES;
  }
  callActionButton_.layer.masksToBounds = YES;
  callActionButton_.layer.cornerRadius = 2.0;
  callActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
  self.descriptionLabel.text = @"75 9th Avenue\nNew York, NY 10011";

  CLLocationCoordinate2D mapCoord = CLLocationCoordinate2DMake(40.741964, -74.004793);
  CGFloat latlLongSpan = 400.0f / 111000.0f;
  MKCoordinateSpan mapSpan = MKCoordinateSpanMake(latlLongSpan, latlLongSpan);
  MKCoordinateRegion region = MKCoordinateRegionMake(mapCoord, mapSpan);
  [self.mapView setRegion:region animated:YES];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  PlaceAnnotation* annotation = [[PlaceAnnotation alloc] initWithLatitude:40.741964
                                                                longitude:-74.004793];
  [self.mapView addAnnotation:annotation];
  [annotation release];
}

#pragma mark - MKMapViewDelegate Methods

- (MKAnnotationView*)mapView:(MKMapView*)theMapView viewForAnnotation:(id<MKAnnotation>)annotation {
  if (![annotation isKindOfClass:[PlaceAnnotation class]])
    return nil;

  MKPinAnnotationView* pinView = [[[MKPinAnnotationView alloc] initWithAnnotation:annotation reuseIdentifier:nil] autorelease];
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.animatesDrop = YES;
  return pinView;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.mainContentView = nil;
  self.mainActionsView = nil;
  self.callActionButton = nil;
  self.callActionLabel = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
}

- (void)dealloc {
  self.mainContentView = nil;
  self.mainActionsView = nil;
  self.callActionButton = nil;
  self.callActionLabel = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  [super dealloc];
}

#pragma mark - Actions

- (IBAction)reservationButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:[NSURL URLWithString:@"http://www.opentable.com/opentables.aspx?t=rest&r=5002"]];
}

- (IBAction)callButtonPressed:(id)sender {
  [self confirmCall];
  
}

- (void)confirmCall {
  UIAlertView* alert = [[UIAlertView alloc] init];
	[alert setTitle:@"(212) 741 5279"];
	[alert setDelegate:self];
	[alert addButtonWithTitle:@"Cancel"];
	[alert addButtonWithTitle:@"Call"];
	[alert show];
	[alert release];
}

- (void)alertView:(UIAlertView*)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
	if (buttonIndex == 1)
		[[UIApplication sharedApplication] openURL:[NSURL URLWithString:@"tel://212-741-5279"]];
}

@end
