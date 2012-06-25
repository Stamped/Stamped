
//
//  STChunkGroup.m
//  Stamped
//
//  Created by Landon Judkins on 6/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STChunkGroup.h"

@implementation STChunkGroup

@synthesize chunks = _chunks;

- (id)initWithChunks:(NSArray *)chunks {
    NSAssert1(chunks.count > 0, @"Chunks count must be > 0: %@", chunks);
    STChunk* first = [chunks objectAtIndex:0];
    STChunk* last = chunks.lastObject;
    CGFloat start = first.start;
    CGFloat end = last.end;
    CGFloat lineHeight = first.lineHeight;
    CGFloat lineLimit = first.lineLimit;
    NSInteger lineCount = 1;
    for (STChunk* chunk in chunks) {
        lineCount += chunk.lineCount - 1;
    }
    self = [super initWithLineHeight:lineHeight start:start end:end width:first.frame.size.width lineCount:lineCount lineLimit:lineLimit];
    if (self) {
        self.topLeft = first.topLeft;
        _chunks = [chunks copy];
    }
    return self;
}

- (id)initWithLineHeight:(CGFloat)lineHeight 
                   start:(CGFloat)start 
                     end:(CGFloat)end
                   width:(CGFloat)width 
               lineCount:(NSInteger)lineCount 
               lineLimit:(NSInteger)limit {
    NSAssert1(NO, @"Don't use %@ with initWithLineHeight", self);
    return nil;
}

- (id)init {
    NSAssert1(NO, @"Don't use %@ with init", self);
    return nil;
}

- (void)dealloc
{
    [_chunks release];
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    for (STChunk* chunk in self.chunks) {
        [chunk drawRect:rect];
    }
}

@end
