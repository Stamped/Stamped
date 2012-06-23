//
//  STChunkGroup.h
//  Stamped
//
//  Created by Landon Judkins on 6/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STChunk.h"

@interface STChunkGroup : STChunk

- (id)initWithChunks:(NSArray*)chunks;

@property (nonatomic, readonly, copy) NSArray* chunks;

@end
