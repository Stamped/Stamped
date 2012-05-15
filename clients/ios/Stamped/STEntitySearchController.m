//
//  STEntitySearchController.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySearchController.h"
#import "Util.h"
#import "STSearchField.h"
#import "UIButton+Stamped.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "CALayer+Stamped.h"
#import "STButton.h"
#import "STStampedAPI.h"
#import "EntityDetailViewController.h"
#import "STEntitySearchSection.h"
#import <CoreLocation/CoreLocation.h>

@interface STEntitySearchTableViewCell : UITableViewCell

+ (NSString*)reuseIdentifier;

- (id)initWithEntitySearchResult:(id<STEntitySearchResult>)searchResult;

@end

@implementation STEntitySearchTableViewCell

+ (NSString*)reuseIdentifier {
  return @"searchCell";
}

- (id)initWithEntitySearchResult:(id<STEntitySearchResult>)result {
  self = [super initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:[STEntitySearchTableViewCell reuseIdentifier]];
  if (self) {
    self.textLabel.text = result.title;
    self.textLabel.font = [UIFont stampedTitleFont];
    self.textLabel.textColor = [UIColor stampedDarkGrayColor];
    self.detailTextLabel.text = result.subtitle;
    self.detailTextLabel.font = [UIFont stampedSubtitleFont];
    self.detailTextLabel.textColor = [UIColor stampedGrayColor];
    self.imageView.image = [Util imageForCategory:result.category];
  }
  return self;
}

@end

@interface STEntitySearchController () <UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate, CLLocationManagerDelegate>

@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* initialQuery;
@property (nonatomic, readwrite, retain) NSArray<STEntitySearchSection>* suggestedSections;
@property (nonatomic, readwrite, retain) NSArray<STEntitySearchResult>* searchResults;
@property (nonatomic, readwrite, retain) UITableView* tableView;

@end

@implementation STEntitySearchController

@synthesize category = category_;
@synthesize initialQuery = initialQuery_;
@synthesize suggestedSections = suggestedSections_;
@synthesize searchResults = searchResults_;
@synthesize tableView = tableView_;

- (id)initWithCategory:(NSString*)category andQuery:(NSString*)query {
  self = [super init];
  if (self) {
    if (!category) {
      category = @"music";
    }
    category_ = [category retain];
    initialQuery_ = [query retain];
    STEntitySuggested* suggested = [[[STEntitySuggested alloc] init] autorelease];
    suggested.category = category;
    CLLocationManager* locationManager = [[CLLocationManager alloc] init];
    locationManager.delegate = self; 
    locationManager.desiredAccuracy = kCLLocationAccuracyBest; 
    locationManager.distanceFilter = kCLDistanceFilterNone; 
    [locationManager startUpdatingLocation];
    [locationManager stopUpdatingLocation];
    CLLocation *location = [locationManager location];
    if (location) {
      float longitude=location.coordinate.longitude;
      float latitude=location.coordinate.latitude;
      suggested.coordinates = [NSString stringWithFormat:@"%f,%f", latitude, longitude];
    }
    [[STStampedAPI sharedInstance] entityResultsForEntitySuggested:suggested 
                                                       andCallback:^(NSArray<STEntitySearchSection> *results, NSError *error, STCancellation* cancellation) {
                                                         if (results) {
                                                           self.suggestedSections = results;
                                                           [self.tableView reloadData];
                                                         }
                                                         else {
                                                           [Util warnWithMessage:[NSString stringWithFormat:@"Entities suggested failed to load with error:\n%@", error] andBlock:nil];
                                                         }
                                                       }];
  }
  return self;
}

- (void)dealloc
{
  [category_ release];
  [initialQuery_ release];
  [super dealloc];
}

- (void)cancelClicked {
  [[Util sharedNavigationController] popViewControllerAnimated:YES];
}

- (void)loadView {
  CGFloat borderSize = 1;
  self.view = [[[UIView alloc] initWithFrame:[Util standardFrameWithNavigationBar:YES]] autorelease];
  UIView* header = [[[UIView alloc] initWithFrame:CGRectMake(-borderSize, -borderSize, self.view.frame.size.width + 2*borderSize, 40+borderSize)] autorelease];
  header.layer.borderWidth = borderSize;
  header.layer.borderColor = [UIColor whiteColor].CGColor;
  header.layer.shadowRadius = 2;
  header.layer.shadowOffset = CGSizeMake(0, 1);
  header.layer.shadowColor = [UIColor blackColor].CGColor;
  header.layer.shadowOpacity = .1;
  [Util addGradientToLayer:header.layer 
                withColors:[NSArray arrayWithObjects:[UIColor colorWithWhite:.95 alpha:1], [UIColor colorWithWhite:.9 alpha:1], nil] 
                  vertical:YES];
  STSearchField* searchField = [[[STSearchField alloc] init] autorelease];
  if (self.initialQuery) {
    searchField.text = self.initialQuery;
  }
  searchField.enablesReturnKeyAutomatically = NO;
  searchField.frame = [Util centeredAndBounded:searchField.frame.size inFrame:header.frame];
  [Util reframeView:searchField withDeltas:CGRectMake(0, 2, 0, 0)];
  searchField.delegate = self;
  CGFloat xPadding = 5;
  CGFloat buttonWidth = 60;
  [Util reframeView:searchField withDeltas:CGRectMake(xPadding, 0, -(xPadding * 3 + buttonWidth), 0)];
  [header addSubview:searchField];
  
  CGRect cancelFrame = [Util centeredAndBounded:CGSizeMake(buttonWidth, searchField.frame.size.height) 
                                        inFrame:CGRectMake(CGRectGetMaxX(searchField.frame) + xPadding, 0, buttonWidth, header.frame.size.height)];
  UIView* cancelViews[2];
  for (NSInteger i = 0; i < 2; i++) {
    UIView* cancelView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, cancelFrame.size.width, cancelFrame.size.height)] autorelease];
    UILabel* label = [Util viewWithText:@"Cancel"
                                   font:[UIFont stampedFontWithSize:14]
                                  color:i == 0 ? [UIColor stampedGrayColor] : [UIColor whiteColor]
                                   mode:UILineBreakModeClip
                             andMaxSize:cancelFrame.size];
    label.frame = [Util centeredAndBounded:label.frame.size inFrame:cancelView.frame];
    [cancelView addSubview:label];
    if (i == 0) {
      [cancelView.layer useStampedButtonNormalStyle];
    }
    else {
      [cancelView.layer useStampedButtonActiveStyle];
    }
    cancelViews[i] = cancelView;
  }
  STButton* cancelButton = [[[STButton alloc] initWithFrame:cancelFrame 
                                                 normalView:cancelViews[0] 
                                                 activeView:cancelViews[1] 
                                                     target:self 
                                                  andAction:@selector(cancelClicked)] autorelease];
  [header addSubview:cancelButton];
  
  
  tableView_ = [[UITableView alloc] initWithFrame:CGRectMake(0, 
                                                             CGRectGetMaxY(header.frame), 
                                                             self.view.frame.size.width, 
                                                             self.view.frame.size.height + [Util sharedNavigationController].navigationBar.frame.size.height - CGRectGetMaxY(header.frame))];
  tableView_.delegate = self;
  tableView_.dataSource = self;
  tableView_.rowHeight = 68;
  //tableView.backgroundColor = [UIColor grayColor];
  [self.view addSubview:tableView_];
  [self.view addSubview:header];
}

- (void)viewWillAppear:(BOOL)animated {
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
}

- (void)viewWillDisappear:(BOOL)animated {
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  NSLog(@"numberOfRows");
  if (self.searchResults) {
    return self.searchResults.count;
  }
  else if (self.suggestedSections) {
    id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
    return sectionObject.entities.count;
  }
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  if (self.searchResults) {
    return 1;
  }
  else if (self.suggestedSections) {
    return self.suggestedSections.count;
  }
  else {
    return 1;
  }
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STEntitySearchResult> result = nil;
  if (self.searchResults) {
    result = [self.searchResults objectAtIndex:indexPath.row];
  }
  else if (self.suggestedSections) {
    id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
    result = [section.entities objectAtIndex:indexPath.row];
  }
  if (result) {
    return [[[STEntitySearchTableViewCell alloc] initWithEntitySearchResult:result] autorelease];
  }
  else {
    return nil;
  }
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STEntitySearchResult> result = nil;
  if (self.searchResults) {
    result = [self.searchResults objectAtIndex:indexPath.row];
  }
  else if (self.suggestedSections) {
    id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
    result = [section.entities objectAtIndex:indexPath.row];
  }
  if (result) {
    EntityDetailViewController* controller = [[[EntityDetailViewController alloc] initWithSearchID:result.searchID] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    NSLog(@"Chose %@, %@", result.title, result.searchID);
  }
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
  if (textField.text && ![textField.text isEqualToString:@""]) {
    STEntitySearch* search = [[[STEntitySearch alloc] init] autorelease];
    search.category = self.category;
    search.query = textField.text;
    [[STStampedAPI sharedInstance] entityResultsForEntitySearch:search andCallback:^(NSArray<STEntitySearchResult> *results, NSError *error) {
      NSLog(@"searchResult:%@",error);
      if (results) {
        for (id<STEntitySearchResult> result in results) {
          NSLog(@"%@", result.title);
        }
        self.searchResults = results;
        [self.tableView reloadData];
      }
    }];
  }
}
- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
  if (self.searchResults) {
    return nil;
  }
  else if (self.suggestedSections) {
    id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
    return sectionObject.name;
  }
  return nil;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  //Override collapsing behavior
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

@end
