//
//  STCreditPickerController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditPickerController.h"

#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "STCreditPill.h"
#import "STCreditTextField.h"
#import "User.h"

@interface STCreditPickerController ()
- (void)addPerson:(NSString*)username;
- (void)removePerson:(NSString*)username;

@property (nonatomic, retain) UITableView* creditTableView;
@property (nonatomic, copy) NSArray* peopleArray;
@end

@implementation STCreditPickerController

@synthesize delegate = delegate_;
@synthesize creditTextField = creditTextField_;
@synthesize creditTableView = creditTableView_;
@synthesize peopleArray = peopleArray_;

- (id)init {
  self = [super init];
  if (self) {
    User* currentUser = [AccountManager sharedManager].currentUser;
    NSFetchRequest* request = [User fetchRequest];
    request.predicate = [NSPredicate predicateWithFormat:@"userID != %@ AND name != NIL", currentUser.userID];
    request.sortDescriptors =
        [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"name" ascending:YES]];
    self.peopleArray = [User objectsWithFetchRequest:request];
  }
  return self;
}

- (void)dealloc {
  self.peopleArray = nil;
  creditTableView_.delegate = nil;
  creditTableView_.dataSource = nil;
  [creditTableView_ release];
  [super dealloc];
}

- (void)setCreditTextField:(STCreditTextField*)creditTextField {
  if (creditTextField_ != creditTextField) {
    creditTextField_.delegate = nil;
    creditTextField_ = creditTextField;
    creditTextField_.delegate = self;
  }
}

- (void)addPerson:(NSString*)username {
  STCreditPill* pill = [[STCreditPill alloc] initWithFrame:CGRectMake(10, 10, 94, 25)];
  pill.textLabel.text = username;
  [pill sizeToFit];
  [creditTextField_ addSubview:pill];
  [pill release];
}

- (void)removePerson:(NSString*)username {
  
}

#pragma mark - UITextFieldDelegate methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  NSString* result = [textField.text stringByReplacingCharactersInRange:range withString:string];
  NSArray* people = [result componentsSeparatedByString:@" "];
  for (NSString* username in people) {
    if (!username.length)
      continue;
    [self addPerson:username];
  }

  NSLog(@"People: %@", people);
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [delegate_ creditTextFieldDidBeginEditing:creditTextField_];
  if (!creditTableView_) {
    creditTableView_ = [[UITableView alloc] initWithFrame:CGRectMake(0, 48, 320, 196)
                                                    style:UITableViewStylePlain];
    creditTableView_.rowHeight = 51.0;
    creditTableView_.delegate = self;
    creditTableView_.dataSource = self;
    creditTableView_.alpha = 0.0;
    // TODO(andybons): MAJOR hack.
    [creditTextField_.superview.superview insertSubview:creditTableView_
                                           belowSubview:creditTextField_.superview];
  }
  [UIView animateWithDuration:0.3 animations:^{
    creditTableView_.alpha = 1.0;
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [delegate_ creditTextFieldDidEndEditing:creditTextField_];
  [UIView animateWithDuration:0.3 animations:^{
    creditTableView_.alpha = 0.0;
  }];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  return [delegate_ creditTextFieldShouldReturn:creditTextField_];
}

#pragma mark - UITableViewDelegate methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  NSLog(@"Selected row...");
  [tableView deselectRowAtIndexPath:indexPath animated:YES];
}

#pragma mark - UITableViewDataSource methods.

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return peopleArray_.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  cell.disclosureArrowHidden = YES;
  cell.user = [self.peopleArray objectAtIndex:indexPath.row];

  return cell;
}

@end
