//
//  STSimpleEntitySearchResult.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STEntitySearchResult.h"

@interface STSimpleEntitySearchResult : NSObject <STEntitySearchResult, NSCoding>

@property (nonatomic, readwrite, copy) NSString* searchID;
@property (nonatomic, readwrite, copy) NSString* title;
@property (nonatomic, readwrite, copy) NSString* subtitle;
@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSNumber* distance;

+ (RKObjectMapping*)mapping;

@end
