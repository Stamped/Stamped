//
//  STTypes.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

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
    STProfileImageSize28 = 28,
    STProfileImageSize31 = 31,
    STProfileImageSize37 = 37,
    STProfileImageSize46 = 46,
    STProfileImageSize55 = 55,
    STProfileImageSize72 = 72,
    STProfileImageSize144 = 144,
} STProfileImageSize;


typedef enum {
    STCategoryIconSize9 = 9,
    STCategoryIconSize15 = 15,
} STCategoryIconSize;