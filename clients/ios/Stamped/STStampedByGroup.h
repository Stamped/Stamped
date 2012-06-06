//
//  STStampedByGroup.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampPreview.h"

@protocol STStampedByGroup <NSObject>

@property (nonatomic, readonly, copy) NSNumber* count;
@property (nonatomic, readonly, retain) NSArray<STStampPreview>* stampPreviews;

@end
