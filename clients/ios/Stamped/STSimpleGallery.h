//
//  STSimpleGallery.h
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STGallery.h"

@interface STSimpleGallery : NSObject <STGallery, NSCoding>

@property (nonatomic, readwrite, copy) NSString* layout;
@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSArray<STImageList>* images;

+ (RKObjectMapping*)mapping;

@end
