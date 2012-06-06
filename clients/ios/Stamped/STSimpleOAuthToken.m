//
//  STSimpleOAuthToken.m
//  Stamped
//
//  Created by Landon Judkins on 6/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleOAuthToken.h"

@implementation STSimpleOAuthToken

@synthesize accessToken = _accessToken;
@synthesize refreshToken = _refreshToken;
@synthesize lifespanInSeconds = _lifespanInSeconds;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _accessToken = [[decoder decodeObjectForKey:@"accessToken"] retain];
        _refreshToken = [[decoder decodeObjectForKey:@"refreshToken"] retain];
        _lifespanInSeconds = [[decoder decodeObjectForKey:@"lifespanInSeconds"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_accessToken release];
    [_refreshToken release];
    [_lifespanInSeconds release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.accessToken forKey:@"accessToken"];
    [encoder encodeObject:self.refreshToken forKey:@"refreshToken"];
    [encoder encodeObject:self.lifespanInSeconds forKey:@"lifespanInSeconds"];
}

+ (RKObjectMapping*)mapping {
    
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    [mapping mapKeyPathsToAttributes:
     @"access_token", @"accessToken",
     @"refresh_token", @"refreshToken",
     @"expires_in", @"lifespanInSeconds",
     nil];
    return mapping;
}

@end
