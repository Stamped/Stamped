//
//  FindFriendsViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "FindFriendsViewController.h"

@implementation FindFriendsViewController

- (id)init {
  if ((self = [self initWithNibName:@"FindFriendsView" bundle:nil])) {
  }
  return self;
}

#pragma mark - View lifecycle

#pragma mark - Actions

- (IBAction)done:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
