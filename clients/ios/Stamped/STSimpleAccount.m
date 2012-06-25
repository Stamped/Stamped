//
//  STSimpleAccount.m
//  Stamped
//
//  Created by Landon Judkins on 6/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleAccount.h"

@implementation STSimpleAccount

@synthesize userID = _userID;
@synthesize name = _name;
@synthesize email = _email;
@synthesize authService = _authService;
@synthesize screenName = _screenName;
@synthesize privacy = _privacy;
@synthesize phone = _phone;

-(id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _userID = [[decoder decodeObjectForKey:@"userID"] retain];
        _name = [[decoder decodeObjectForKey:@"name"] retain];
        _email = [[decoder decodeObjectForKey:@"email"] retain];
        _authService = [[decoder decodeObjectForKey:@"authService"] retain];
        _screenName = [[decoder decodeObjectForKey:@"screenName"] retain];
        _privacy = [[decoder decodeObjectForKey:@"privacy"] retain];
        _phone = [[decoder decodeObjectForKey:@"phone"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_userID release];
    [_name release];
    [_email release];
    [_authService release];
    [_screenName release];
    [_privacy release];
    [_phone release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.userID forKey:@"userID"];
    [encoder encodeObject:self.name forKey:@"name"];
    [encoder encodeObject:self.email forKey:@"email"];
    [encoder encodeObject:self.authService forKey:@"authService"];
    [encoder encodeObject:self.screenName forKey:@"screenName"];
    [encoder encodeObject:self.privacy forKey:@"privacy"];
    [encoder encodeObject:self.phone forKey:@"phone"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPathsToAttributes:
     @"user_id", @"userID",
     @"name", @"name",
     @"email", @"email",
     @"auth_service", @"authService",
     @"screen_name", @"screenName",
     @"privacy", @"privacy",
     @"phone", @"phone",
     nil];
    
    return mapping;
}

@end
