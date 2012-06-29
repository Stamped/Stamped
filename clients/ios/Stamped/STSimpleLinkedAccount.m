//
//  STSimpleLinkedAccount.m
//  Stamped
//
//  Created by Landon Judkins on 6/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleLinkedAccount.h"

@implementation STSimpleLinkedAccount

@synthesize serviceName = _serviceName;
@synthesize linkedUserID = _linkedUserID;
@synthesize linkedScreenName = _linkedScreenName;
@synthesize linkedName = _linkedName;
@synthesize token = _token;
@synthesize secret = _secret;
@synthesize tokenExpiration = _tokenExpiration;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _serviceName = [[decoder decodeObjectForKey:@"serviceName"] retain];
        _linkedUserID = [[decoder decodeObjectForKey:@"linkedUserID"] retain];
        _linkedScreenName = [[decoder decodeObjectForKey:@"linkedScreenName"] retain];
        _linkedName = [[decoder decodeObjectForKey:@"linkedName"] retain];
        _token = [[decoder decodeObjectForKey:@"token"] retain];
        _secret = [[decoder decodeObjectForKey:@"secret"] retain];
        _tokenExpiration = [[decoder decodeObjectForKey:@"tokenExpiration"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_serviceName release];
    [_linkedUserID release];
    [_linkedScreenName release];
    [_linkedName release];
    [_token release];
    [_secret release];
    [_tokenExpiration release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.serviceName forKey:@"serviceName"];
    [encoder encodeObject:self.linkedUserID forKey:@"linkedUserID"];
    [encoder encodeObject:self.linkedScreenName forKey:@"linkedName"];
    [encoder encodeObject:self.token forKey:@"token"];
    [encoder encodeObject:self.secret forKey:@"secret"];
    [encoder encodeObject:self.tokenExpiration forKey:@"tokenExpiration"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPathsToAttributes:
     @"service_name", @"serviceName",
     @"linked_user_id", @"linkedUserID",
     @"linked_name", @"linked_name",
     @"token", @"token",
     @"secret", @"secret",
     @"token_expiration", @"tokenExpiration",
     nil];
    
    return mapping;
}

@end
