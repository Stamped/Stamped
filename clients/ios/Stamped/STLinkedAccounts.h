//
//  STLinkedAccounts.h
//  Stamped
//
//  Created by Landon Judkins on 6/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STLinkedAccount.h"

@protocol STLinkedAccounts <NSObject>

@property (nonatomic, readonly, retain) id<STLinkedAccount> facebook;
@property (nonatomic, readonly, retain) id<STLinkedAccount> twitter;
@property (nonatomic, readonly, retain) id<STLinkedAccount> rdio;
@property (nonatomic, readonly, retain) id<STLinkedAccount> spotify;
@property (nonatomic, readonly, retain) id<STLinkedAccount> netflix;

@end

