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

#import "DetailedEntity.h"
#import "Entity.h"
#import "STPlaceAnnotation.h"
#import "Util.h"
#import "MusicDetailViewController.h"

@interface OtherDetailViewController ()
- (void)confirmCall;
- (void)addAnnotation;
- (void)setupMainActionsContainer;
- (void)setupMapView;
- (void)setupSectionViews;
- (void)loadAppImage;
- (void)setupAsAppDetail;
@end

@implementation OtherDetailViewController

@synthesize callActionButton = callActionButton_;
@synthesize callActionLabel = callActionLabel_;
@synthesize mapView = mapView_;
@synthesize mapContainerView = mapContainerView_;
@synthesize appActionsView = appActionsView_;

#pragma mark - View lifecycle

- (void)showContents {
  self.descriptionLabel.text = detailedEntity_.subtitle;
  if ([detailedEntity_.subcategory.lowercaseString isEqualToString:@"app"]) {
    [self loadAppImage];
  } else {
    [self setupMainActionsContainer];
    [self setupMapView];
    [self setupSectionViews];
  }
}

- (void)viewDidLoad {
  self.mainActionsView.hidden = YES;
  callActionButton_.hidden = YES;
  callActionLabel_.hidden = YES;
  [super viewDidLoad];
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
  pinView.animatesDrop = YES;
  pinView.pinColor = MKPinAnnotationColorRed;
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
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.imageView.delegate = nil;
  self.imageView = nil;
  self.appActionsView = nil;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.mainContentView = nil;
  self.callActionButton = nil;
  self.callActionLabel = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.imageView.delegate = nil;
  self.imageView = nil;
  self.appActionsView = nil;
  [super dealloc];
}

#pragma mark - Actions

- (IBAction)callButtonPressed:(id)sender {
  [self confirmCall];
}

- (void)confirmCall {
  UIAlertView* alert = [[UIAlertView alloc] init];
  [alert setTitle:detailedEntity_.phone];
  [alert setDelegate:self];
  [alert addButtonWithTitle:@"Cancel"];
  [alert addButtonWithTitle:@"Call"];
  [alert show];
  [alert release];
}

- (void)alertView:(UIAlertView*)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 1) {
    NSString* telURL = [NSString stringWithFormat:@"tel://%i",
                        [Util sanitizedPhoneNumberFromString:detailedEntity_.phone]];
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:telURL]];
  }
}

#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {  
  callActionButton_.layer.masksToBounds = YES;
  callActionButton_.layer.cornerRadius = 2.0;
  callActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
  
  if (detailedEntity_.phone) {  
    callActionLabel_.text = detailedEntity_.phone;
    callActionButton_.hidden = NO;
    callActionLabel_.hidden = NO;
    self.mainActionsView.hidden = NO;
  }

  // TODO(andybons): Will there EVER be a phone property for Other category?
  if (!detailedEntity_.phone) {
    mapContainerView_.frame = CGRectOffset(mapContainerView_.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
  }  
}

- (void)setupMapView {
  if (!detailedEntity_.coordinates)
    return;

  NSArray* coordinates = [detailedEntity_.coordinates componentsSeparatedByString:@","]; 
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
  
  if (mapContainerView_.hidden == YES) {
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -self.mapContainerView.frame.size.height);
  }
  
  
  if (detailedEntity_.desc && detailedEntity_.desc.length > 0) {
    [self addSectionWithName:@"Description"];
    section = [sectionsDict_ objectForKey:@"Description"];
    [section addText:detailedEntity_.desc forKey:@"desc"];
  }

  
  section = [self makeSectionWithName:@"Information"];
  
  if (detailedEntity_.subcategory && detailedEntity_.subcategory.length > 0) { 
    [section addPairedLabelWithName:@"Category:"
                              value:detailedEntity_.subcategory.capitalizedString
                             forKey:@"subcategory"];
  }
  
  
  if (detailedEntity_.address && detailedEntity_.address.length > 0) {
    [section addPairedLabelWithName:@"Address:"
                              value:detailedEntity_.address
                             forKey:@"address"];
  }
    
  if (detailedEntity_.neighborhood && detailedEntity_.neighborhood.length > 0) {
    [section addPairedLabelWithName:@"Neighborhood:"
                              value:detailedEntity_.neighborhood.capitalizedString
                             forKey:@"neighborhood"];
  }
  
  if (detailedEntity_.website && detailedEntity_.website.length > 0) {
    [section addPairedLabelWithName:@"Website:"
                              value:detailedEntity_.website
                             forKey:@"website"];
  }
  
  if (section.contentDict.objectEnumerator.allObjects.count > 0) {
    [self addSection:section];
    self.mainContentView.hidden = NO;
  }
  
  NSSet* stamps = entityObject_.stamps;
  
  if (stamps && stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO;
  }
}


- (void)loadAppImage {
  if (detailedEntity_.image && detailedEntity_.image.length > 0) {
    self.imageView.imageURL = detailedEntity_.image;
    self.imageView.delegate = self;
    self.imageView.hidden = NO;
    self.imageView.contentMode = UIViewContentModeScaleAspectFit;
    self.imageView.layer.masksToBounds = YES;
    self.imageView.layer.cornerRadius = 18.0;
  }
}

- (void)setupAsAppDetail {
  self.mainActionsView.hidden = YES;
  self.imageView.hidden = NO;
  
  // Set up actions container (download link)
  if (detailedEntity_.itunesShortURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.appActionsView.hidden = NO;
  } else {
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.appActionsView.frame));
  }
  
  // Add content sections
  self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -self.mapContainerView.frame.size.height);
  CollapsibleViewController* section;
  if (detailedEntity_.desc && detailedEntity_.desc.length > 0) {
    [self addSectionWithName:@"Description"];
    section = [sectionsDict_ objectForKey:@"Description"];
    [section addText:detailedEntity_.desc forKey:@"desc"];
    self.mainContentView.hidden = NO;
  }
  
  // Add also stamped by
  NSSet* stamps = entityObject_.stamps;
  if (stamps && stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO;
  }
  
  // Because clipping the imageview to bounds, which is necessary for rounded corners, hides the shadow.
  UIView* shadowView = [[UIImageView alloc] initWithFrame:self.imageView.frame];
  shadowView.backgroundColor = [UIColor clearColor];
  shadowView.layer.cornerRadius = 18.0;
  shadowView.layer.shadowColor = [UIColor blackColor].CGColor;
  shadowView.layer.shadowOffset = CGSizeMake(0.0, 3.0);
  shadowView.layer.shadowRadius = 3.0;
  shadowView.layer.shadowOpacity = 0.3;
  shadowView.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:shadowView.bounds cornerRadius:18.0].CGPath;
  [self.scrollView insertSubview:shadowView belowSubview:self.imageView];
  [shadowView.layer setNeedsDisplay];
  [shadowView release];

  self.imageView.layer.shadowOpacity = 0;
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:[NSURL URLWithString:detailedEntity_.itunesShortURL]];
}

- (void)STImageView:(STImageView*)imageView didLoadImage:(UIImage*)image {
  [self setupAsAppDetail];
}


@end
