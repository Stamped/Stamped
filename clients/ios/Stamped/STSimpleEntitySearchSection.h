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

@interface STSimpleEntitySearchSection : NSObject <STEntitySearchSection>

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSArray<STEntitySearchResult>* results;

+ (RKObjectMapping*)mapping;

@end
