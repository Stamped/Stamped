//
//  STMapViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 BONS - Ask about caching
 */

#import <MapKit/MapKit.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STMapScopeSlider.h"

typedef enum {
  STMapViewControllerSourceInbox,
  STMapViewControllerSourceTodo,
  STMapViewControllerSourceUser
} STMapViewControllerSource;

@class STSearchField;
@class STToolbar;
@class User;

@interface STLegacyMapViewController : UIViewController <MKMapViewDelegate,
                                                   UITextFieldDelegate,
                                                   NSFetchedResultsControllerDelegate,
                                                   UIAlertViewDelegate,
                                                   STMapScopeSliderDelegate,
                                                   RKObjectLoaderDelegate>

@property (nonatomic, assign) STMapViewControllerSource source;
@property (nonatomic, retain) User* user;
@property (nonatomic, retain) IBOutlet STMapScopeSlider* scopeSlider;
@property (nonatomic, retain) IBOutlet UIView* overlayView;
@property (nonatomic, retain) IBOutlet UIButton* locationButton;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;
@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet STToolbar* toolbar;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;

- (void)reset;
- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)locationButtonPressed:(id)sender;

@end
