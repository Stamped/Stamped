//
//  STMapViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

typedef enum {
  STMapViewControllerSourceInbox,
  STMapViewControllerSourceTodo,
  STMapViewControllerSourceUser
} STMapViewControllerSource;

@class STSearchField;

@interface STMapViewController : UIViewController <MKMapViewDelegate,
                                                   UITextFieldDelegate,
                                                   NSFetchedResultsControllerDelegate>

@property (nonatomic, assign) STMapViewControllerSource source;
@property (nonatomic, retain) IBOutlet UIView* overlayView;
@property (nonatomic, retain) IBOutlet UIButton* locationButton;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;
@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) IBOutlet MKMapView* mapView;

- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)locationButtonPressed:(id)sender;

@end
