//
//  STOAuthToken.h
//  Stamped
//
//  Created by Landon Judkins on 6/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STOAuthToken <NSObject>

@property (nonatomic, readonly, copy) NSString* accessToken;
@property (nonatomic, readonly, copy) NSString* refreshToken;
@property (nonatomic, readonly, copy) NSNumber* lifespanInSeconds;

@end
