//
//  STLinkedAccount.h
//  Stamped
//
//  Created by Landon Judkins on 6/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STLinkedAccount <NSObject>

@property (nonatomic, readonly, copy) NSString* serviceName;
@property (nonatomic, readonly, copy) NSString* linkedUserID;
@property (nonatomic, readonly, copy) NSString* linkedScreenName;
@property (nonatomic, readonly, copy) NSString* linkedName;
@property (nonatomic, readonly, copy) NSString* token;
@property (nonatomic, readonly, copy) NSString* secret;
@property (nonatomic, readonly, copy) NSDate* tokenExpiration;

@end
