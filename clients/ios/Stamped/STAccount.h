//
//  STAccount.h
//  Stamped
//
//  Created by Landon Judkins on 6/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STAccount <NSObject>

@property (nonatomic, readonly, copy) NSString* userID;
@property (nonatomic, readonly, copy) NSString* name;
@property (nonatomic, readonly, copy) NSString* email;
@property (nonatomic, readonly, copy) NSString* authService;
@property (nonatomic, readonly, copy) NSString* screenName;
@property (nonatomic, readonly, copy) NSNumber* privacy;
@property (nonatomic, readonly, copy) NSString* phone;

@end
