//
//  STSimpleUser.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleUser.h"

@implementation STSimpleUser

@synthesize name = _name;
@synthesize userID = _userID;
@synthesize screenName = _screenName;
@synthesize primaryColor = _primaryColor;
@synthesize secondaryColor = _secondaryColor;
@synthesize privacy = _privacy;
@synthesize imageURL = _imageURL;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _name = [[decoder decodeObjectForKey:@"name"] retain];
        _userID = [[decoder decodeObjectForKey:@"userID"] retain];
        _screenName = [[decoder decodeObjectForKey:@"screenName"] retain];
        _primaryColor = [[decoder decodeObjectForKey:@"primaryColor"] retain];
        _secondaryColor = [[decoder decodeObjectForKey:@"secondaryColor"] retain];
        _privacy = [[decoder decodeObjectForKey:@"privacy"] retain];
        _imageURL = [[decoder decodeObjectForKey:@"imageURL"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_name release];
    [_userID release];
    [_screenName release];
    [_primaryColor release];
    [_secondaryColor release];
    [_privacy release];
    [_imageURL release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.name forKey:@"name"];
    [encoder encodeObject:self.userID forKey:@"userID"];
    [encoder encodeObject:self.screenName forKey:@"screenName"];
    [encoder encodeObject:self.primaryColor forKey:@"primaryColor"];
    [encoder encodeObject:self.secondaryColor forKey:@"secondaryColor"];
    [encoder encodeObject:self.privacy forKey:@"privacy"];
    [encoder encodeObject:self.imageURL forKey:@"imageURL"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleUser class]];
    
    [mapping mapKeyPathsToAttributes:
     @"user_id", @"userID",
     @"screen_name", @"screenName",
     @"color_primary", @"primaryColor",
     @"color_secondary", @"secondaryColor",
     @"image_url", @"imageURL",
     nil];
    
    [mapping mapAttributes:
     @"name",
     @"privacy",
     nil];
    
    return mapping;
}

+ (STSimpleUser*)userFromLegacyUser:(User*)legacyUser {
    if (legacyUser == nil) {
        return nil;
    }
    STSimpleUser* user = [[[STSimpleUser alloc] init] autorelease];
    user.name = legacyUser.name;
    user.userID = legacyUser.userID;
    user.screenName = legacyUser.screenName;
    user.primaryColor = legacyUser.primaryColor;
    user.secondaryColor = legacyUser.secondaryColor;
    user.imageURL = legacyUser.imageURL;
    return user;
}


@end
