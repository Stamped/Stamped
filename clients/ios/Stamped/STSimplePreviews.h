//
//  STSimplePreviews.h
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STPreviews.h"

@interface STSimplePreviews : NSObject <STPreviews>

@property (nonatomic, readwrite, copy) NSArray<STUser>* todos;
@property (nonatomic, readwrite, copy) NSArray<STUser>* likes;
@property (nonatomic, readwrite, copy) NSArray<STComment>* comments;
@property (nonatomic, readwrite, copy) NSArray<STStamp>* credits;

+ (RKObjectMapping*)mapping;

+ (STSimplePreviews*)previewsWithPreviews:(id<STPreviews>)previews;

@end
