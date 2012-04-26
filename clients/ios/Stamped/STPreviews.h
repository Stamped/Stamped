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

@protocol STPreviews <NSObject>

@property (nonatomic, readonly, copy) NSArray<STUser>* todos;
@property (nonatomic, readonly, copy) NSArray<STUser>* likes;
@property (nonatomic, readonly, copy) NSArray<STComment>* comments;

@end
