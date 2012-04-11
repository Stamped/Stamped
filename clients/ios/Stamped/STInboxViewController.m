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

@interface STInboxViewController () <UIPickerViewDelegate, UIPickerViewDataSource>

- (void)categoryChanged:(id)category;

@property (nonatomic, readonly, retain) STMultipleChoiceButton* categoryButton;
@property (nonatomic, readonly, retain) STStampsView* stampsView;
@property (nonatomic, readonly, retain) UITextField* queryField;


@end

@implementation STInboxViewController

@synthesize categoryButton = _categoryButton;
@synthesize stampsView = _stampsView;
@synthesize queryField = _queryField;

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
  _stampsView = [[STStampsView alloc] initWithFrame:CGRectMake(0, 0, 320, 363)];
  //view.backgroundColor = [UIColor redColor];
  STGenericCollectionSlice* slice = [[STGenericCollectionSlice alloc] init];
  slice.offset = [NSNumber numberWithInt:0];
  slice.limit = [NSNumber numberWithInt:NSIntegerMax];
  slice.sort = @"created";
  _stampsView.slice = slice;
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_stampsView];
  
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
  self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Map"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(rightButtonClicked:)] autorelease];
}

- (void)backButtonClicked:(id)button {
  [[STRootMenuView sharedInstance] toggle];
}


- (void)rightButtonClicked:(id)button {
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
  STGenericCollectionSlice* slice = self.stampsView.slice;
  if (slice.category != category && ![slice.category isEqualToString:category]) {
    slice.category = category;
    self.stampsView.slice = slice;
  }
  //UINavigationController* controller = [Util sharedNavigationController];
  //self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"test" style:UIBarButtonItemStylePlain target:self action:@selector(backButtonClicked:)] autorelease];
  
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
  [super textFieldDidEndEditing:textField];
  NSString* query = textField.text;
  STGenericCollectionSlice* slice = self.stampsView.slice;
  if ([query isEqualToString:@""]) {
    if (slice.query) {
      slice.query = nil;
      slice.sort = @"created";
      self.stampsView.slice = slice;
    }
  }
  else {
    if (![slice.query isEqualToString:query]) {
      slice.query = query;
      slice.sort = @"relevance";
      self.stampsView.slice = slice;
    }
  }
}

@end
