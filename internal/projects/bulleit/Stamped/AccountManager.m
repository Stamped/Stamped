//
//  AccountManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "AccountManager.h"

#import <RestKit/CoreData/CoreData.h>

static NSString* kCurrentUserIDKey = @"com.stamped.CurrentUserID";
static AccountManager* sharedAccountManager_ = nil;

@interface AccountManager ()
- (void)showAuthAlert;
@end

@implementation AccountManager

@synthesize currentUser = currentUser_;
@synthesize delegate = delegate_;

+ (AccountManager*)sharedManager {
  if (sharedAccountManager_ == nil)
    sharedAccountManager_ = [[super allocWithZone:NULL] init];
  
  return sharedAccountManager_;
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedManager] retain];
}

- (id)copyWithZone:(NSZone*)zone {
  return self;
}

- (id)retain {
  return self;
}

- (NSUInteger)retainCount {
  return NSUIntegerMax;
}

- (oneway void)release {
  // Do nothin'.
}

- (id)autorelease {
  return self;
}

#pragma mark - Begin custom implementation.

- (void)showAuthAlert {
  UIAlertView* alertView = [[UIAlertView alloc] initWithTitle:@"Enter username"
                                                     message:@"\n"
                                                    delegate:self
                                           cancelButtonTitle:@"Cancel"
                                           otherButtonTitles:@"Go", nil];
  UITextField* usernameField = [[UITextField alloc] initWithFrame:CGRectMake(16, 45, 252, 25)];
  usernameField.borderStyle = UITextBorderStyleRoundedRect;
  usernameField.autocapitalizationType = UITextAutocapitalizationTypeNone;
  usernameField.autocorrectionType = UITextAutocorrectionTypeNo;
  usernameField.keyboardAppearance = UIKeyboardAppearanceAlert;
  usernameField.delegate = self;
  [usernameField becomeFirstResponder];
  [alertView addSubview:usernameField];
  [usernameField release];

  [alertView show];
  [alertView release];
}

- (void)authenticate {
  if (currentUser_)
    return;

  // Check the defaults for the user ID.
  NSString* userID = [[NSUserDefaults standardUserDefaults] stringForKey:kCurrentUserIDKey];
  if (userID) {
    NSLog(@"User id stored: %@", userID);
    NSFetchRequest* request = [User fetchRequest];
    NSPredicate* predicate = [NSPredicate predicateWithFormat:@"userID == %@", userID];
    [request setPredicate:predicate];

    NSArray* results = [User objectsWithFetchRequest:request];
    if (results.count > 0) {
      self.currentUser = [results objectAtIndex:0];
      [self.delegate accountManagerDidAuthenticate];
      return;
    }
  }

  [self showAuthAlert];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [self showAuthAlert];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  if (object == nil) {
    [self showAuthAlert];
    return;
  }

  self.currentUser = object;
  [[NSUserDefaults standardUserDefaults] setObject:self.currentUser.userID forKey:kCurrentUserIDKey];
  [[NSUserDefaults standardUserDefaults] synchronize];
  [self.delegate accountManagerDidAuthenticate];
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidEndEditing:(UITextField*)textField {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider objectMappingForKeyPath:@"User"];
  NSString* resourcePath = [NSString stringWithFormat:@"/users/lookup.json?screen_names=%@", textField.text];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:userMapping
                                  delegate:self];
}

@end
