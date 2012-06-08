//
//  STChunksView.m
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STChunksView.h"
#import "STChunk.h"

@interface STChunksViewInner : UIView

@property (nonatomic, readonly, copy) NSArray* chunks;

@end

@implementation STChunksViewInner

@synthesize chunks = _chunks;

- (id)initWithChunks:(NSArray *)chunks
{
    CGFloat maxX = 0;
    CGFloat maxY = 0;
    for (STChunk* chunk in chunks) {
        maxX = MAX(CGRectGetMaxX(chunk.frame), maxX);
        maxY = MAX(CGRectGetMaxY(chunk.frame) + chunk.lineHeight, maxY);
    }
    self = [super initWithFrame:CGRectMake(0, 0, maxX, maxY)];
    if (self) {
        _chunks = [chunks copy];
        self.backgroundColor = [UIColor clearColor];
    }
    return self;
}

- (void)drawRect:(CGRect)rect
{
    for (STChunk* chunk in self.chunks) {
        [chunk drawRect:rect];
    }
}


@end

@implementation STChunksView

- (id)initWithChunks:(NSArray *)chunks
{
    CGFloat maxX = 0;
    CGFloat maxY = 0;
    for (STChunk* chunk in chunks) {
        maxX = MAX(CGRectGetMaxX(chunk.frame), maxX);
        maxY = MAX(CGRectGetMaxY(chunk.frame), maxY);
    }
    self = [super initWithFrame:CGRectMake(0, 0, maxX, maxY)];
    if (self) {
        UIView* innerView = [[[STChunksViewInner alloc] initWithChunks:chunks] autorelease];
        [self addSubview:innerView];
        self.backgroundColor = [UIColor clearColor];
        self.clipsToBounds = NO;
    }
    return self;
}


@end
