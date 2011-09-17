//
//  SearchEntitiesViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "SearchEntitiesTableViewCell.h"
#import "STSearchField.h"
#import "SearchResult.h"

static NSString* const kSearchPath = @"/entities/search.json";

@interface SearchEntitiesViewController ()
- (void)textFieldDidChange:(id)sender;
- (void)sendSearchRequest;

@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, retain) CLLocationManager* locationManager;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@end

@implementation SearchEntitiesViewController

@synthesize resultsArray = resultsArray_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;
@synthesize locationManager = locationManager_;
@synthesize addStampCell = addStampCell_;
@synthesize addStampLabel = addStampLabel_;
@synthesize tooltipImageView = tooltipImageView_;
@synthesize searchingIndicatorView = searchingIndicatorView_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.view.backgroundColor = [UIColor colorWithWhite:0.972 alpha:1.0];
  self.cancelButton.layer.masksToBounds = YES;
  self.cancelButton.layer.borderColor = [UIColor colorWithWhite:0.6 alpha:0.8].CGColor;
  self.cancelButton.layer.borderWidth = 1.0;
  self.cancelButton.layer.cornerRadius = 5.0;
  self.cancelButton.layer.shadowOpacity = 1.0;

  [self.searchField addTarget:self
                       action:@selector(textFieldDidChange:)
             forControlEvents:UIControlEventEditingChanged];

  self.locationManager = [[[CLLocationManager alloc] init] autorelease];
  
  tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_tooltip"]];
  tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame, 6, 40);
  tooltipImageView_.alpha = 0.0;
  [self.view addSubview:tooltipImageView_];
  [tooltipImageView_ release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.searchField = nil;
  self.locationManager.delegate = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorView = nil;
  tooltipImageView_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self.locationManager startUpdatingLocation];
  [self.searchField becomeFirstResponder];
  if (self.searchField.text.length == 0) {
    [UIView animateWithDuration:0.3 animations:^{
      tooltipImageView_.alpha = 1.0;
    }];
  }
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:NO animated:animated];
  [self.locationManager stopUpdatingLocation];
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)cancelButtonTapped:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  NSInteger numRows = [resultsArray_ count];
  if (self.searchField.text.length > 0)
    ++numRows;  // One more for the 'Add new entity' cell.

  return numRows;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == [resultsArray_ count])
    return self.addStampCell;
  
  static NSString* CellIdentifier = @"ResultCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[SearchEntitiesTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  [(SearchEntitiesTableViewCell*)cell setSearchResult:((SearchResult*)[resultsArray_ objectAtIndex:indexPath.row])];
  
  return cell;
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != searchField_)
    return YES;

  [self sendSearchRequest];
  [searchField_ resignFirstResponder];
  return NO;
}

- (void)sendSearchRequest {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* searchResultMapping = [objectManager.mappingProvider mappingForKeyPath:@"SearchResult"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kSearchPath delegate:self];
  objectLoader.objectMapping = searchResultMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithKeysAndObjects:@"q", searchField_.text, nil];
  if (self.locationManager.location) {
    CLLocationCoordinate2D coordinate = self.locationManager.location.coordinate;
    NSString* coordString = [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
    [params setObject:coordString forKey:@"coordinates"];
  }
  objectLoader.params = params;
  searchingIndicatorView_.hidden = NO;
  [objectLoader send];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  searchingIndicatorView_.hidden = YES;
  NSLog(@"Response: %@", objectLoader.response.bodyAsString);
  self.resultsArray = objects;
  [self.tableView reloadData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  searchingIndicatorView_.hidden = YES;

  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];

  [searchField_ becomeFirstResponder];
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  SearchResult* result = nil;
  if (indexPath.row == [resultsArray_ count]) {
    result = [[[SearchResult alloc] init] autorelease];
    result.title = self.searchField.text;
  } else {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row];
  }
  
  CreateStampViewController* detailViewController =
      [[CreateStampViewController alloc] initWithSearchResult:result];
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (void)textFieldDidChange:(id)sender {
  if (sender != self.searchField)
    return;

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     tooltipImageView_.alpha = self.searchField.text.length > 0 ? 0.0 : 1.0;
                   }
                   completion:nil];

  self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
  if (searchField_.text.length > 3) {
    [self sendSearchRequest];
  } else if (searchField_.text.length == 0) {
    [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
    searchingIndicatorView_.hidden = YES;
  }
}

@end
