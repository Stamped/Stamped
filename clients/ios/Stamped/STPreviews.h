//
//  STPreviews.h
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUser.h"
#import "STComment.h"
#import "STStampPreview.h"

@protocol STStamp;

@protocol STPreviews <NSObject>

@property (nonatomic, readonly, copy) NSArray<STUser>* todos;
@property (nonatomic, readonly, copy) NSArray<STUser>* likes;
@property (nonatomic, readonly, copy) NSArray<STComment>* comments;
@property (nonatomic, readonly, copy) NSArray<STStampPreview>* credits;
@property (nonatomic, readonly, copy) NSArray<STStampPreview>* stamps;

@end
