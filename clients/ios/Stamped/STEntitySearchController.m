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

@interface STEntitySearchController () <UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate>

@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* initialQuery;
@property (nonatomic, readwrite, retain) NSArray<STEntitySearchResult>* suggestedResults;
@property (nonatomic, readwrite, retain) NSArray<STEntitySearchResult>* searchResults;
@property (nonatomic, readwrite, retain) UITableView* tableView;

@end

@implementation STEntitySearchController

@synthesize category = category_;
@synthesize initialQuery = initialQuery_;
@synthesize suggestedResults = suggestedResults_;
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
    STEntitySuggested* suggested = [[STEntitySuggested alloc] init];
    suggested.category = category;
    [[STStampedAPI sharedInstance] entityResultsForEntitySuggested:suggested andCallback:^(NSArray<STEntitySearchResult> *results, NSError *error) {
      for (id<STEntitySearchResult> result in results) {
        NSLog(@"%@", result.title);
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
                                                                     self.view.frame.size.height - CGRectGetMaxY(header.frame))];
  tableView_.delegate = self;
  tableView_.dataSource = self;
  //tableView.backgroundColor = [UIColor grayColor];
  [self.view addSubview:tableView_];
  [self.view addSubview:header];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  NSLog(@"numberOfRows");
  if (self.searchResults) {
    return self.searchResults.count;
  }
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"test"] autorelease];
  id<STEntitySearchResult> result = [self.searchResults objectAtIndex:indexPath.row];
  cell.textLabel.text = result.title;
  return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STEntitySearchResult> result = [self.searchResults objectAtIndex:indexPath.row];
  EntityDetailViewController* controller = [[[EntityDetailViewController alloc] initWithSearchID:result.searchID] autorelease];
  [[Util sharedNavigationController] pushViewController:controller animated:YES];
  NSLog(@"Chose %@, %@", result.title, result.searchID);
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

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  //Override collapsing behavior
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

@end
