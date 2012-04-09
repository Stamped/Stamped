//
//  STCommentSlice.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCollectionSlice.h"

@interface STCommentSlice : STGenericCollectionSlice

@property (nonatomic, readwrite, copy) NSString* stampID;

+ (STCommentSlice*)sliceForStampID:(NSString*)stampID offset:(NSInteger)offset limit:(NSInteger)limit;

@end
