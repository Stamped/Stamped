//
//  STSimpleMetadata.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMetadata.h"

@interface STSimpleMetadata : NSObject<STMetadata>

@property (nonatomic, readwrite, assign) NSInteger name;
@property (nonatomic, readwrite, retain) NSArray<STMetadataItem>* data;

+ (RKObjectMapping*)mapping;

@end
