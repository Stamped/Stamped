//
//  STCreditPickerController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditPickerController.h"

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "STCreditPill.h"
#import "STCreditTextField.h"
#import "User.h"

@interface STCreditPickerController ()
- (void)addPerson:(NSString*)username;
- (void)removePerson:(NSString*)username;
- (void)decorateTextField;
- (void)resizeTableView;
- (void)filterPeople;

@property (nonatomic, retain) UITableView* creditTableView;
@property (nonatomic, copy) NSArray* peopleArray;
@property (nonatomic, copy) NSArray* filteredPeopleArray;
@property (nonatomic, retain) NSMutableArray* pills;
@end

@implementation STCreditPickerController

@synthesize delegate = delegate_;
@synthesize creditTextField = creditTextField_;
@synthesize creditTableView = creditTableView_;
@synthesize peopleArray = peopleArray_;
@synthesize filteredPeopleArray = filteredPeopleArray_;
@synthesize pills = pills_;

- (id)init {
  self = [super init];
  if (self) {
    self.pills = [NSMutableArray array];
    User* currentUser = [AccountManager sharedManager].currentUser;
    NSSortDescriptor* sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                                     ascending:YES 
                                                                      selector:@selector(localizedCaseInsensitiveCompare:)];
    self.peopleArray = [currentUser.following sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
    [self filterPeople];
  }
  return self;
}

- (void)dealloc {
  self.peopleArray = nil;
  self.filteredPeopleArray = nil;
  self.pills = nil;
  creditTextField_.delegate = nil;
  creditTextField_ = nil;
  creditTableView_.delegate = nil;
  creditTableView_.dataSource = nil;
  [creditTableView_ release];
  creditTableView_ = nil;
  [super dealloc];
}

- (void)setCreditTextField:(STCreditTextField*)creditTextField {
  if (creditTextField_ != creditTextField) {
    creditTextField_ = creditTextField;
    creditTextField_.delegate = self;
    [creditTableView_ release];
    creditTableView_ = nil;
    
    [self decorateTextField];
  }
}

- (void)addPerson:(NSString*)username {
  [pills_.lastObject setHighlighted:NO];

  STCreditPill* pill = [[STCreditPill alloc] initWithFrame:CGRectZero];
  User* user = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", username]];
  pill.textLabel.text = username;
  if (user)
    pill.stampImageView.image = [user stampImageWithSize:StampImageSize14];

  [pill sizeToFit];
  [creditTextField_ addSubview:pill];
  [creditTextField_ sizeToFit];
  [self performSelector:@selector(resizeTableView) withObject:nil afterDelay:0.0];
  [pills_ addObject:pill];
  [pill release];
}

- (void)removePerson:(NSString*)username {
  STCreditPill* pillToRemove = nil;
  for (STCreditPill* pill in pills_) {
    if ([pill.textLabel.text isEqualToString:username]) {
      pillToRemove = pill;
      break;
    }
  }
  if (!pillToRemove)
    return;

  [pillToRemove removeFromSuperview];
  [pills_ removeObject:pillToRemove];
  [creditTextField_ setNeedsLayout];
  for (STCreditPill* pill in pills_)
    pill.highlighted = NO;

  [self performSelector:@selector(resizeTableView) withObject:nil afterDelay:0.0];
}

- (NSString*)usersSeparatedByCommas {
  if (!pills_.count)
    return nil;

  NSMutableArray* usersArray = [NSMutableArray arrayWithCapacity:pills_.count];
  for (STCreditPill* pill in pills_)
    [usersArray addObject:pill.textLabel.text];
  return [usersArray componentsJoinedByString:@","];
}

- (void)decorateTextField {
  // Take raw text and convert it into pills.
  NSString* text = [creditTextField_.text stringByReplacingOccurrencesOfString:@"\u200b" withString:@""];
  text = [text stringByReplacingOccurrencesOfString:@"@" withString:@""]; 
  NSArray* people = [text componentsSeparatedByString:@" "];
  for (NSString* username in people) {
    if (!username.length)
      continue;
    
    [self addPerson:username];
  }
  creditTextField_.text = @"\u200b";
}

- (void)resizeTableView {
  creditTableView_.frame = CGRectMake(0,
                                      CGRectGetMaxY(creditTextField_.frame) + 1,
                                      320,
                                      460 - CGRectGetHeight(creditTextField_.frame) - 216);
  [creditTableView_ setNeedsDisplay];
}

- (void)filterPeople {
  NSString* text = [creditTextField_.text stringByReplacingOccurrencesOfString:@"\u200b" withString:@""];
  text = [text stringByReplacingOccurrencesOfString:@"@" withString:@""];
  if (text.length) {
    NSPredicate* p = [NSPredicate predicateWithFormat:@"(userID != %@ AND name != NIL) AND ((name contains[cd] %@) OR (screenName contains[cd] %@))",
        [AccountManager sharedManager].currentUser.userID, text, text];
    
    self.filteredPeopleArray = [peopleArray_ filteredArrayUsingPredicate:p];
  } else {
    self.filteredPeopleArray = peopleArray_;
  }
  [creditTableView_ reloadData];
}

#pragma mark - UITextFieldDelegate methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  if ([string isEqualToString:@" "]) {
    if (!textField.hidden) {
      [self decorateTextField];
      [self performSelector:@selector(filterPeople) withObject:nil afterDelay:0.0];
    } else {
      textField.hidden = NO;
      for (STCreditPill* pill in pills_)
        pill.highlighted = NO;
    }
    return NO;
  }
  NSString* result = [textField.text stringByReplacingCharactersInRange:range withString:string];
  if (result.length == 0 && pills_.count) {
    if (textField.hidden) {
      // Remove the last pill (the one highlighted).
      [self removePerson:[pills_.lastObject textLabel].text];
      textField.hidden = NO;
    } else {
      // Last pill should be highlighted.
      [pills_.lastObject setHighlighted:YES];
      textField.hidden = YES;
    }
    [self performSelector:@selector(filterPeople) withObject:nil afterDelay:0.0];
    return NO;
  }
  textField.hidden = NO;
  for (STCreditPill* pill in pills_)
    pill.highlighted = NO;
  
  [creditTextField_ setNeedsLayout];
  [self performSelector:@selector(filterPeople) withObject:nil afterDelay:0.0];
  [self performSelector:@selector(resizeTableView) withObject:nil afterDelay:0.0];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [delegate_ creditTextFieldDidBeginEditing:creditTextField_];
  if (!creditTableView_) {
    creditTableView_ = [[UITableView alloc] initWithFrame:CGRectZero
                                                    style:UITableViewStylePlain];
    creditTableView_.rowHeight = 52.0;
    creditTableView_.delegate = self;
    creditTableView_.dataSource = self;
    creditTableView_.alpha = 0.0;
    [creditTextField_.superview insertSubview:creditTableView_ belowSubview:creditTextField_];
    [self resizeTableView];
  }
  creditTableView_.contentOffset = CGPointZero;
  [UIView animateWithDuration:0.3 animations:^{
    creditTableView_.alpha = 1.0;
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [self decorateTextField];
  [(id)delegate_ performSelector:@selector(creditTextFieldDidEndEditing:)
                      withObject:creditTextField_
                      afterDelay:0.0];
  [UIView animateWithDuration:0.3 animations:^{
    creditTableView_.alpha = 0.0;
  }];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  return [delegate_ creditTextFieldShouldReturn:creditTextField_];
}

#pragma mark - UITableViewDelegate methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  User* user = [filteredPeopleArray_ objectAtIndex:indexPath.row];
  [self addPerson:user.screenName];
  creditTextField_.text = @"\u200b";
  [tableView deselectRowAtIndexPath:indexPath animated:YES];
  [self performSelector:@selector(filterPeople) withObject:nil afterDelay:0.3];
}

#pragma mark - UITableViewDataSource methods.

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return filteredPeopleArray_.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  cell.disclosureArrowHidden = YES;
  cell.user = [self.filteredPeopleArray objectAtIndex:indexPath.row];

  return cell;
}

@end
