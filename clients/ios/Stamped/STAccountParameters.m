//
//  STAccountParameters.m
//  Stamped
//
//  Created by Landon Judkins on 6/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAccountParameters.h"

@implementation STAccountParameters

@synthesize screenName = _screenName;
@synthesize name = _name;
@synthesize email = _email;
@synthesize phone = _phone;
@synthesize tempImageURL = _tempImageURL;
@synthesize bio = _bio;
@synthesize website = _website;
@synthesize location = _location;
@synthesize primaryColor = _primaryColor;
@synthesize secondaryColor = _secondaryColor;

- (void)dealloc {
    [_screenName release];
    [_name release];
    [_email release];
    [_phone release];
    [_tempImageURL release];
    [_bio release];
    [_website release];
    [_location release];
    [_primaryColor release];
    [_secondaryColor release];
    [super dealloc];
}

- (NSMutableDictionary *)asDictionaryParams {
    NSMutableDictionary* params = [[NSMutableDictionary alloc] init];
    NSDictionary* mapping = [NSDictionary dictionaryWithObjectsAndKeys:
                             @"screen_name", @"screenName",
                             @"name", @"name",
                             @"email", @"email",
                             @"phone", @"phone",
                             @"temp_image_url", @"tempImageURL",
                             @"bio", @"bio",
                             @"website", @"website",
                             @"location", @"location",
                             @"color_primary", @"primaryColor",
                             @"color_secondary", @"secondaryColor",
                             nil];
    for (NSString* key in mapping.allKeys) {
        id object = [self valueForKey:key];
        if (object != nil) {
            [params setObject:object forKey:[mapping objectForKey:key]];
        }
    }
    return [params autorelease];
}

- (NSString*)errorStringRequiresEmail:(BOOL)requiresEmail {
    
    if (!_screenName || [_screenName stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length==0) {
        return @"No username.";
    } else if (!_name || [_name stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length==0) {
        return @"No name.";
    } else if (requiresEmail && (!_email || [_email stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length==0)) {
        return @"No email.";
    }
    
    return nil;
    
}

- (NSString*)description {
    return [NSString stringWithFormat:@"%@ name: %@ screenname: %@ email: %@ phone: %@ bio: %@ imageurl : %@ colors: %@ %@", [super description], _name, _screenName, _email, _phone, _bio, _tempImageURL, _primaryColor, _secondaryColor];
}

@end
