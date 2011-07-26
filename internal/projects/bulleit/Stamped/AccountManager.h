//
//  AccountManager.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "User.h"

@protocol AccountManagerDelegate
@required
- (void)accountManagerDidAuthenticate;
@end

@interface AccountManager : NSObject<UITextFieldDelegate, RKObjectLoaderDelegate>

+ (AccountManager*)sharedManager;
- (void)authenticate;

@property (nonatomic, retain) User* currentUser;
@property (nonatomic, assign) id<AccountManagerDelegate> delegate;

@end
