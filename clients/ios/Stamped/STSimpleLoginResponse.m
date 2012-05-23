//
//  STSimpleLoginResponse.m
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleLoginResponse.h"

@implementation STSimpleLoginResponse

@synthesize userID = _userID;
@synthesize token = _token;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _userID = [[decoder decodeObjectForKey:@"userID"] retain];
        _token = [[decoder decodeObjectForKey:@"token"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_userID release];
    [_token release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.userID forKey:@"userID"];
    [encoder encodeObject:self.token forKey:@"token"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleLoginResponse class]];
    
    [mapping mapKeyPathsToAttributes:
     @"user_id", @"userID",
     nil];
    
    [mapping mapAttributes:
     @"token",
     nil];
    
    return mapping;
}

@end
