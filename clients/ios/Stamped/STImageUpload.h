//
//  STImageUpload.h
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampedParameter.h"

@interface STImageUpload : STStampedParameter

@property (nonatomic, readwrite, copy) NSString* tempImageURL;
@property (nonatomic, readwrite, copy) NSNumber* tempImageWidth;
@property (nonatomic, readwrite, copy) NSNumber* tempImageHeight;

@end
