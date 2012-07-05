//
//  STSimpleUser.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleUser.h"
#import "STStampedAPI.h"
#import "STEvents.h"

@implementation STSimpleUser

@synthesize name = _name;
@synthesize userID = _userID;
@synthesize screenName = _screenName;
@synthesize primaryColor = _primaryColor;
@synthesize secondaryColor = _secondaryColor;
@synthesize privacy = _privacy;
@synthesize imageURL = _imageURL;
@synthesize following = _following;

@synthesize loading=_loading;


- (id)initWithCoder:(NSCoder *)decoder {
    NSString* userID = [decoder decodeObjectForKey:@"userID"];
    NSAssert1(userID, @"UserID should not be none for %@", self);
    id<STUser> cachedUser = [[STStampedAPI sharedInstance] cachedUserForUserID:userID];
    if (cachedUser) {
        [self autorelease];
        return (id)[cachedUser retain];
    }
    else {
        self = [super init];
        if (self) {
            _name = [[decoder decodeObjectForKey:@"name"] retain];
            _userID = [userID retain];
            _screenName = [[decoder decodeObjectForKey:@"screenName"] retain];
            _primaryColor = [[decoder decodeObjectForKey:@"primaryColor"] retain];
            _secondaryColor = [[decoder decodeObjectForKey:@"secondaryColor"] retain];
            _privacy = [[decoder decodeObjectForKey:@"privacy"] retain];
            _imageURL = [[decoder decodeObjectForKey:@"imageURL"] retain];
            _following = [[decoder decodeObjectForKey:@"following"] retain];
            [[STStampedAPI sharedInstance] cacheUser:self];
        }
        return self;
    }
}

- (void)dealloc {
    [_name release];
    [_userID release];
    [_screenName release];
    [_primaryColor release];
    [_secondaryColor release];
    [_privacy release];
    [_imageURL release];
    [_following release];
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
    [encoder encodeObject:self.following forKey:@"following"];
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
     @"following",
     nil];
    
    return mapping;
}

- (void)toggleFollowing {
    
    if ([self.following boolValue]) {
        
        [[STStampedAPI sharedInstance] removeFriendForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
            self.following = [NSNumber numberWithBool:![self.following boolValue]];
            [STEvents postEvent:EventTypeUserFollowToggleFinished identifier:self.userID object:self.following];
            _loading = NO;
        }];
        
    } 
    else {
        
        [[STStampedAPI sharedInstance] addFriendForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
            self.following = [NSNumber numberWithBool:![self.following boolValue]];
            [STEvents postEvent:EventTypeUserFollowToggleFinished identifier:self.userID object:self.following];
            _loading = NO;
        }];
        
    }
    
}


@end
