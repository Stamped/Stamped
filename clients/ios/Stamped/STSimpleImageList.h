//
//  STSimpleImageList.h
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STImageList.h"

@interface STSimpleImageList : NSObject <STImageList>

@property (nonatomic, readwrite, copy) NSArray<STImage>* sizes;
@property (nonatomic, readwrite, copy) NSString* caption;
@property (nonatomic, readwrite, retain) id<STAction> action;

+ (RKObjectMapping*)mapping;

@end
