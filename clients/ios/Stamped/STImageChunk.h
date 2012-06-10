//
//  STImageChunk.h
//  Stamped
//
//  Created by Landon Judkins on 6/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STChunk.h"

@interface STImageChunk : STChunk

- (id)initWithPrev:(STChunk*)prev andFrame:(CGRect)frame;

@property (nonatomic, readwrite, retain) UIImage* image;

@end
