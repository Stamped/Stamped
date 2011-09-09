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

#import "Entity.h"
#import "STPlaceAnnotation.h"

@interface PlaceDetailViewController ()
- (void)confirmCall;
- (void)addAnnotation;
@end

@implementation PlaceDetailViewController

@synthesize mainContentView = mainContentView_;
@synthesize callActionButton = callActionButton_;
@synthesize callActionLabel = callActionLabel_;
@synthesize mapView = mapView_;

#pragma mark - View lifecycle

- (void)showContents {
  self.descriptionLabel.text = [entityObject_.address stringByReplacingOccurrencesOfString:@", "
                                                                                withString:@"\n"];
  self.mainActionsView.hidden = entityObject_.openTableURL == nil;
  if (self.mainActionsView.hidden) {
    mainContentView_.frame = CGRectOffset(mainContentView_.frame, 0,
                                          -CGRectGetHeight(self.mainActionsView.frame));
  }
  callActionButton_.layer.masksToBounds = YES;
  callActionButton_.layer.cornerRadius = 2.0;
  callActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
  callActionLabel_.text = [entityObject_ localizedPhoneNumber];

  callActionButton_.hidden = YES;

  if (!entityObject_.coordinates)
    return;

  NSArray* coordinates = [entityObject_.coordinates componentsSeparatedByString:@","]; 
  latitude_ = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  longitude_ = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  CLLocationCoordinate2D mapCoord = CLLocationCoordinate2DMake(latitude_, longitude_);
  MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kStandardLatLongSpan, kStandardLatLongSpan);
  MKCoordinateRegion region = MKCoordinateRegionMake(mapCoord, mapSpan);
  self.mainContentView.hidden = NO;
  [self.mapView setRegion:region animated:YES];

  if (viewIsVisible_ && !annotation_)
    [self addAnnotation];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (dataLoaded_ && !annotation_)
    [self addAnnotation];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  if (annotation_) {
    [self.mapView removeAnnotation:annotation_];
    annotation_ = nil;
  }
}

- (void)addAnnotation {
  annotation_ = [[STPlaceAnnotation alloc] initWithLatitude:latitude_ longitude:longitude_];
  [self.mapView addAnnotation:annotation_];
  [annotation_ release];
}

#pragma mark - MKMapViewDelegate Methods

- (MKAnnotationView*)mapView:(MKMapView*)theMapView viewForAnnotation:(id<MKAnnotation>)annotation {
  if (![annotation isKindOfClass:[STPlaceAnnotation class]])
    return nil;

  MKPinAnnotationView* pinView = [[[MKPinAnnotationView alloc] initWithAnnotation:annotation reuseIdentifier:nil] autorelease];
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.animatesDrop = YES;
  return pinView;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.mainContentView = nil;
  self.callActionButton = nil;
  self.callActionLabel = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
}

- (void)dealloc {
  self.mainContentView = nil;
  self.callActionButton = nil;
  self.callActionLabel = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  [super dealloc];
}

#pragma mark - Actions

- (IBAction)reservationButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:[NSURL URLWithString:entityObject_.openTableURL]];
}

- (IBAction)callButtonPressed:(id)sender {
  [self confirmCall];
}

- (void)confirmCall {
  UIAlertView* alert = [[UIAlertView alloc] init];
	[alert setTitle:[entityObject_ localizedPhoneNumber]];
	[alert setDelegate:self];
	[alert addButtonWithTitle:@"Cancel"];
	[alert addButtonWithTitle:@"Call"];
	[alert show];
	[alert release];
}

- (void)alertView:(UIAlertView*)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
	if (buttonIndex == 1) {
    NSString* telURL = [NSString stringWithFormat:@"tel://%i", entityObject_.phone];
		[[UIApplication sharedApplication] openURL:[NSURL URLWithString:telURL]];
  }
}
@end
