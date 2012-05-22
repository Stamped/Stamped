//
//  STSimpleImage.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STImage.h"

@interface STSimpleImage : NSObject <STImage, NSCoding>

@property (nonatomic, readwrite, copy) NSString* url;
@property (nonatomic, readwrite, copy) NSNumber* width;
@property (nonatomic, readwrite, copy) NSNumber* height;
@property (nonatomic, readwrite, copy) NSString* source;
@property (nonatomic, readwrite, copy) NSString* filter;

+ (RKObjectMapping*)mapping;

@end
