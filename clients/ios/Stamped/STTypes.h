//
//  STTypes.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 Definitions of globally used enumerations and types.
 
 Notes:
 This header is intended to be a leaf that imports no other Stamped specific headers.
 
 TODOs:
 Remove deprecated FriendsOfFriends scope
 
 2012-08-10
 -Landon
 */

#import <Foundation/Foundation.h>

typedef void (^STCallback)(void);

// All sizes are expressed in points.
typedef enum {
    STStampImageSize12 = 12,
    STStampImageSize14 = 14,
    STStampImageSize16 = 16,
    STStampImageSize18 = 18,
    STStampImageSize28 = 28,
    STStampImageSize32 = 32,
    STStampImageSize42 = 42,
    STStampImageSize46 = 46,
    STStampImageSize60 = 60,
    STStampImageSize270 = 270
} STStampImageSize;

// These are represented using points, but downscaling is handled for
// non-retina displays.
typedef enum {
    STProfileImageSize24 = 24,
    STProfileImageSize48 = 48,
    STProfileImageSize60 = 60,
    STProfileImageSize96 = 96,
    STProfileImageSize144 = 144,
} STProfileImageSize;


typedef enum {
    STCategoryIconSize9 = 9,
    STCategoryIconSize15 = 15,
} STCategoryIconSize;


typedef enum {
    STStampedAPIScopeYou = 0,
    STStampedAPIScopeFriends,
    STStampedAPIScopeEveryone,
    STStampedAPIScopeFriendsOfFriends,
} STStampedAPIScope;
