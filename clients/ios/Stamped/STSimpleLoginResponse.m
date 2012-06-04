//
//  STSimpleLoginResponse.m
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleLoginResponse.h"
#import "STSimpleUserDetail.h"

@implementation STSimpleLoginResponse

@synthesize user = _user;
@synthesize token = _token;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _user = [[decoder decodeObjectForKey:@"user"] retain];
        _token = [[decoder decodeObjectForKey:@"token"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_user release];
    [_token release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.user forKey:@"user"];
    [encoder encodeObject:self.token forKey:@"token"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleLoginResponse class]];
    
    [mapping mapAttributes:
     @"token",
     nil];
    
    [mapping mapRelationship:@"user" withMapping:[STSimpleUserDetail mapping]];
    
    return mapping;
}

@end
