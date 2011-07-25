//
//  CreateStampViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "CreateStampDetailViewController.h"
#import "CreateStampTableViewCell.h"
#import "Entity.h"

@interface CreateStampViewController ()
- (void)loadEntitiesFromDataStore;
- (void)textFieldDidChange:(id)sender;

@property (nonatomic, copy) NSArray* entitiesArray;
@property (nonatomic, copy) NSArray* filteredEntitiesArray;
@end

@implementation CreateStampViewController

@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;


- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

- (void)dealloc {
  self.searchField = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  [super dealloc];
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

  self.searchField.leftViewMode = UITextFieldViewModeAlways;
  UIView* leftView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 32, CGRectGetHeight(self.searchField.frame))];
  UIImageView* searchIcon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_icon"]];
  searchIcon.frame = CGRectOffset(searchIcon.frame, 10, 8);
  searchIcon.contentMode = UIViewContentModeCenter;
  [leftView addSubview:searchIcon];
  [searchIcon release];
  self.searchField.leftView = leftView;
  [leftView release];
  self.searchField.contentMode = UIViewContentModeScaleAspectFit;
  [self loadEntitiesFromDataStore];
  [self.searchField addTarget:self
                       action:@selector(textFieldDidChange:)
             forControlEvents:UIControlEventEditingChanged];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.searchField = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self.searchField becomeFirstResponder];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)cancelButtonTapped:(id)sender {
  if ([self respondsToSelector:@selector(presentingViewController)])
    [self.presentingViewController dismissModalViewControllerAnimated:YES];
  else
    [self.parentViewController dismissModalViewControllerAnimated:YES];
}

#pragma mark - Core Data Shiz.

- (void)loadEntitiesFromDataStore {
  self.entitiesArray = nil;
  self.entitiesArray = [Entity objectsWithFetchRequest:[Entity fetchRequest]];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return [filteredEntitiesArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"EntityCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[CreateStampTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  [(CreateStampTableViewCell*)cell setEntityObject:((Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row])];
  
  return cell;
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Entity* entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];
  CreateStampDetailViewController* detailViewController =
      [[CreateStampDetailViewController alloc] initWithEntity:entityObject];
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (void)textFieldDidChange:(id)sender {
  if (sender == self.searchField) {
    NSPredicate* searchPredicate =
        [NSPredicate predicateWithFormat:@"title contains[cd] %@", self.searchField.text];
    self.filteredEntitiesArray = nil;
    self.filteredEntitiesArray = [self.entitiesArray filteredArrayUsingPredicate:searchPredicate];
    [self.tableView reloadData];
  }
}

@end
