//
//  STSimpleEntitySearchSection.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STEntitySearchSection.h"

@interface STSimpleEntitySearchSection : NSObject <STEntitySearchSection, NSCoding>

@property (nonatomic, readwrite, copy) NSString* title;
@property (nonatomic, readwrite, copy) NSString* subtitle;
@property (nonatomic, readwrite, copy) NSString* imageURL;
@property (nonatomic, readwrite, copy) NSArray<STEntitySearchResult>* entities;

+ (RKObjectMapping*)mapping;

@end
