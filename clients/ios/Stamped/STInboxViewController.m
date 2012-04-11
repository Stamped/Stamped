//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STStampsView.h"
#import "STMultipleChoiceButton.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "Util.h"
#import "STRootMenuView.h"
#import "STMapViewController.h"
#import "STInboxScopeSlider.h"
#import "STToolbarView.h"
#import "STStampsViewSource.h"
#import "STFriendsOfFriendsSource.h"
#import "STSuggestedSource.h"
#import "STUserSource.h"
#import "SearchEntitiesViewController.h"

@interface STInboxViewController () <UIPickerViewDelegate, UIPickerViewDataSource, STScopeSliderDelegate>

- (void)categoryChanged:(id)category;
- (void)updateSource;

@property (nonatomic, readonly, retain) STMultipleChoiceButton* categoryButton;
@property (nonatomic, readonly, retain) UITableView* stampsView;
@property (nonatomic, readonly, retain) UITextField* queryField;
@property (nonatomic, readonly, retain) NSDictionary* inboxSources;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSString* query;

@end

@implementation STInboxViewController

@synthesize categoryButton = _categoryButton;
@synthesize stampsView = _stampsView;
@synthesize queryField = _queryField;
@synthesize inboxSources = _inboxSources;
@synthesize scope = _scope;
@synthesize category = _category;
@synthesize query = _query;

static STInboxViewController* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STInboxViewController alloc] init];
}

+ (STInboxViewController*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super init];
  if (self) {
    //pass
  }
  return self;
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  // UIPickerView* picker = [[[UIPickerView alloc] initWithFrame:CGRectMake(0, 0, 320, 20)] autorelease];
  //picker.delegate = self;
  //picker.dataSource = self;
  //[self.scrollView appendChildView:picker];
  UIView* searchBar = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 40)] autorelease];
  NSArray* categories = [NSArray arrayWithObjects:@"None",@"Music",@"Food",@"Book",@"Film",@"Other", nil];
  _categoryButton = [[STMultipleChoiceButton alloc] initWithTitle:nil
                                                          message:nil
                                                          choices:categories 
                                                         andFrame:CGRectMake(5, 5, 80, 30)];
  //_categoryButton.titleLabel.font = [UIFont stampedFontWithSize:16];
  //_categoryButton.titleLabel.textColor = [UIColor stampedDarkGrayColor];
  //_categoryButton.backgroundColor = [UIColor colorWithWhite:.7 alpha:.8];
  [searchBar addSubview:_categoryButton];
  _queryField = [[UITextField alloc] initWithFrame:CGRectMake(90, 5, 225, 30)];
  _queryField.backgroundColor = [UIColor whiteColor];
  _queryField.delegate = self;
  //_queryField.se
  [searchBar addSubview:_queryField];
  searchBar.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
  [self.scrollView appendChildView:searchBar];
  [_categoryButton setTarget:self withSelector:@selector(categoryChanged:)];
  _stampsView = [[UITableView alloc] initWithFrame:CGRectMake(0, 0, 320, 323)];
  //view.backgroundColor = [UIColor redColor];
  self.scope = STStampedAPIScopeFriends;
  _inboxSources = [[NSDictionary dictionaryWithObjectsAndKeys:
                   [[[STStampsViewSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeFriends],
                   [[[STUserSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeYou],
                   [[[STFriendsOfFriendsSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeFriendsOfFriends],
                   [[[STSuggestedSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeEveryone],
                   nil] retain];
  
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_stampsView];
  
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
  self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"+"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(rightButtonClicked:)] autorelease];
  STInboxScopeSlider* slider = [[[STInboxScopeSlider alloc] initWithFrame:CGRectMake(25, 15, 230, 23)] autorelease];
  slider.delegate = self;
  STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
  [toolbar addSubview:slider];
  UIButton* mapButton = [[[UIButton alloc] initWithFrame:CGRectMake(275, 10, 34, 30)] autorelease];
  //mapButton.titleLabel.text = @"Map";
  [mapButton setImage:[UIImage imageNamed:@"nav_map_button"] forState:UIControlStateNormal];
  [mapButton addTarget:self action:@selector(mapButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
  [toolbar addSubview:mapButton];
  [self setToolbar:toolbar withAnimation:NO];
  [self updateSource];
}

- (void)backButtonClicked:(id)button {
  [[STRootMenuView sharedInstance] toggle];
}


- (void)rightButtonClicked:(id)button {
  UINavigationController* controller = [Util sharedNavigationController];
  [controller pushViewController:[[[SearchEntitiesViewController alloc] initWithNibName:@"SearchEntitiesViewController" bundle:nil] autorelease]
                        animated:YES];
}

- (void)mapButtonClicked:(id)button {
  UINavigationController* controller = [Util sharedNavigationController];
  [controller pushViewController:[[[STMapViewController alloc] init] autorelease] animated:YES];
}


- (void)viewDidUnload
{
  [super viewDidUnload];
  [_categoryButton release];
  [_stampsView release];
  [_queryField release];
}

- (NSInteger)numberOfComponentsInPickerView:(UIPickerView *)pickerView {
  return 1;
}

- (NSInteger)pickerView:(UIPickerView *)pickerView numberOfRowsInComponent:(NSInteger)component {
  return 10;
}

- (void)pickerView:(UIPickerView *)pickerView didSelectRow:(NSInteger)row inComponent:(NSInteger)component {
  NSLog(@"selected:%d,%d",row,component);
}

- (NSString *)pickerView:(UIPickerView *)pickerView titleForRow:(NSInteger)row forComponent:(NSInteger)component {
  return [NSString stringWithFormat:@"Row:%d",row];
}

- (CGFloat)pickerView:(UIPickerView *)pickerView rowHeightForComponent:(NSInteger)component {
  return 50;
}

- (CGFloat)pickerView:(UIPickerView *)pickerView widthForComponent:(NSInteger)component {
  return 100;
}

- (void)categoryChanged:(id)category {
  category = [category lowercaseString];
  category = [category isEqualToString:@"none"] ? nil : category;
  self.category = category;
  [self updateSource];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
  [super textFieldDidEndEditing:textField];
  self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
  [self updateSource];
}

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {
  [Util executeOnMainThread:^{
    self.query = textField.text;
  }];
  return YES;
}

- (void)scopeSlider:(STInboxScopeSlider*)slider didChangeGranularity:(STScopeSliderGranularity)granularity {
  //TODO switch to new enum
  self.scope = granularity;
  [self updateSource];
}

- (void)reloadStampedData {
  [self updateSource];
}

- (void)updateSource {
  @try {
    STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
    [slice retain];
    slice.offset = [NSNumber numberWithInt:0];
    slice.limit = [NSNumber numberWithInt:NSIntegerMax];
    slice.category = self.category;
    slice.sort = @"created";
    slice.query = self.query;
    if (slice.query) {
      slice.sort = @"relevance";
    }
    for (STStampsViewSource* old in [self.inboxSources allValues]) {
      old.table = nil;
    }
    STStampsViewSource* source = [self.inboxSources objectForKey:[NSNumber numberWithInt:self.scope]];
    source.table = self.stampsView;
    source.slice = slice;
    
  }
  @catch (NSException *exception) {
    [Util logOperationException:exception withMessage:nil];
  }
  @finally {
    
  }
}

@end
