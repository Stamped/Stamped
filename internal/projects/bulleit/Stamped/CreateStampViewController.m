//
//  CreateStampViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "CreateStampTableViewCell.h"

@implementation CreateStampViewController

@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;

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

  self.searchField.leftViewMode = UITextFieldViewModeAlways;
  UIView* leftView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 28, CGRectGetHeight(self.searchField.frame))];
  UIImageView* searchIcon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_icon"]];
  searchIcon.frame = CGRectOffset(searchIcon.frame, 10, 8);
  searchIcon.contentMode = UIViewContentModeCenter;
  [leftView addSubview:searchIcon];
  [searchIcon release];
  self.searchField.leftView = leftView;
  [leftView release];
  self.searchField.contentMode = UIViewContentModeScaleAspectFit;
  
  // Uncomment the following line to preserve selection between presentations.
  // self.clearsSelectionOnViewWillAppear = NO;

  // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
  // self.navigationItem.rightBarButtonItem = self.editButtonItem;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.searchField = nil;
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
  [self.presentingViewController dismissModalViewControllerAnimated:YES];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 0;
}

- (UITableViewCell *)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[CreateStampTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
    cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  }
  
  // Configure the cell...
  
  return cell;
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  // Navigation logic may go here. Create and push another view controller.
  /*
   <#DetailViewController#> *detailViewController = [[<#DetailViewController#> alloc] initWithNibName:@"<#Nib name#>" bundle:nil];
   // ...
   // Pass the selected object to the new view controller.
   [self.navigationController pushViewController:detailViewController animated:YES];
   [detailViewController release];
   */
}

#pragma mark - UITextFieldDelegate Methods.

- (void)selectionDidChange:(id<UITextInput>)textInput {

}

- (void)selectionWillChange:(id<UITextInput>)textInput {

}

- (void)textDidChange:(id<UITextInput>)textInput {

}

- (void)textWillChange:(id<UITextInput>)textInput {

}

@end
