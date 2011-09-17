//
//  PlaceDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "OtherDetailViewController.h"

#import <CoreLocation/CoreLocation.h>
#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "STPlaceAnnotation.h"

@interface OtherDetailViewController ()
- (void)confirmCall;
- (void)addAnnotation;
- (void)setupMainActionsContainer;
- (void)setupMapView;
- (void)setupSectionViews;
@end

@implementation OtherDetailViewController

@synthesize callActionButton = callActionButton_;
@synthesize callActionLabel = callActionLabel_;
@synthesize mapView = mapView_;
@synthesize mapContainerView = mapContainerView_;

#pragma mark - View lifecycle

- (void)showContents
{
  self.descriptionLabel.text = entityObject_.subtitle;
  
  
  //  NSLog(@"%@", entityObject_);
  
  [self setupMainActionsContainer];
  [self setupMapView];
  [self setupSectionViews];
}

- (void)viewDidLoad {
  self.mainActionButton.hidden = YES;
  self.mainActionLabel.hidden  = YES;
  self.mainActionsView.hidden  = YES;
  callActionButton_.hidden    = YES;
  callActionLabel_.hidden     = YES;
  [super viewDidLoad];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  self.categoryImageView.image = [UIImage imageNamed:@"sort_icon_food_0"];
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


#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  
  callActionButton_.layer.masksToBounds = YES;
  callActionButton_.layer.cornerRadius = 2.0;
  callActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
  
  if (entityObject_.openTableURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden  = NO;
    self.mainActionsView.hidden  = NO;
  }
  
  if (entityObject_.localizedPhoneNumber) {  
    callActionLabel_.text = entityObject_.localizedPhoneNumber;
    callActionButton_.hidden    = NO;
    callActionLabel_.hidden     = NO;
    self.mainActionsView.hidden = NO;
  }
  
  
  if (!entityObject_.openTableURL && (!entityObject_.phone || entityObject_.phone.intValue == 0) ) {
    mapContainerView_.frame = CGRectOffset(mapContainerView_.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
  }  
  
}


- (void)setupMapView {
  if (!entityObject_.coordinates)
    return;
  
  NSArray* coordinates = [entityObject_.coordinates componentsSeparatedByString:@","]; 
  latitude_ = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  longitude_ = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  CLLocationCoordinate2D mapCoord = CLLocationCoordinate2DMake(latitude_, longitude_);
  MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kStandardLatLongSpan, kStandardLatLongSpan);
  MKCoordinateRegion region = MKCoordinateRegionMake(mapCoord, mapSpan);
  mapContainerView_.hidden = NO;
  [self.mapView setRegion:region animated:YES];
  
  if (viewIsVisible_ && !annotation_)
    [self addAnnotation];
}

- (void)setupSectionViews {
  // Information
  // TODO: What if there's no information?
  
  // Description
  
  CollapsibleViewController* section;
  
  if (mapContainerView_.hidden == YES) 
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -self.mapContainerView.frame.size.height);
  
  
  if (entityObject_.desc) {
    [self addSectionWithName:@"Description"];
    section = [sectionsDict_ objectForKey:@"Description"];
    [section addText:entityObject_.desc forKey:@"desc"];
  }

  
  [self addSectionWithName:@"Information"];
  section = [sectionsDict_ objectForKey:@"Information"];
  
  if (entityObject_.subcategory) { 
    [section addPairedLabelWithName:@"Category:"
                              value:entityObject_.subcategory
                             forKey:@"subcategory"];
  }
  
  
  if (entityObject_.address) {
    [section addPairedLabelWithName:@"Address:"
                              value:entityObject_.address
                             forKey:@"address"];

  }
    
  if (entityObject_.neighborhood) {
    [section addPairedLabelWithName:@"Neighborhood:"
                              value:entityObject_.neighborhood
                             forKey:@"neighborhood"];
  }
  
  if (entityObject_.website) {
    [section addPairedLabelWithName:@"Website:"
                              value:entityObject_.website
                             forKey:@"website"];
  }

  NSSet* stamps = entityObject_.stamps;
  
  if (stamps && stamps.count > 0)
    [self addSectionStampedBy];
  
}


@end
