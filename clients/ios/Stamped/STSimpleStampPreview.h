//
//  STSimpleStampPreview.h
//  Stamped
//
//  Created by Landon Judkins on 5/31/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STStampPreview.h"

@interface STSimpleStampPreview : NSObject <STStampPreview, NSCoding>

@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, retain) id<STUser> user;

+ (RKObjectMapping*)mapping;

@end
