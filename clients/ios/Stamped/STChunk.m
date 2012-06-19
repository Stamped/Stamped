//
//  STChunk.m
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STChunk.h"

@implementation STChunk

@synthesize lineHeight = _lineHeight;
@synthesize start = _start;
@synthesize end = _end;
@synthesize lineCount = _lineCount;
@synthesize frame = _frame;
@synthesize lineLimit = _lineLimit;

/*
 
 @property (nonatomic, readonly, assign) CGFloat lineHeight;
 @property (nonatomic, readonly, assign) CGFloat start;
 @property (nonatomic, readonly, assign) CGFloat end;
 @property (nonatomic, readonly, assign) NSInteger lineCount;
 @property (nonatomic, readonly, assign) CGRect frame;
 @property (nonatomic, readonly, assign) NSInteger lineLimit;
 @property (nonatomic, readwrite, assign) CGPoint topLeft;
 @property (nonatomic, readwrite, assign) CGPoint topRight;
 @property (nonatomic, readwrite, assign) CGPoint bottomLeft;
 @property (nonatomic, readwrite, assign) CGPoint bottomRight;
 
 */

- (id)initWithLineHeight:(CGFloat)lineHeight 
                   start:(CGFloat)start 
                     end:(CGFloat)end
                   width:(CGFloat)width 
               lineCount:(NSInteger)lineCount 
               lineLimit:(NSInteger)limit {
    self = [super init];
    if (self) {
        _lineHeight = lineHeight;
        _start = start;
        _end = end;
        _lineCount = lineCount;
        _lineLimit = limit;
        _frame = CGRectMake(0, 0, width, _lineHeight * _lineCount);
    }
    return self;
}

+ (STChunk*)newlineChunkWithPrev:(STChunk*)chunk {
    STChunk* newlineChunk = [[[STChunk alloc] initWithLineHeight:chunk.lineHeight
                                                           start:chunk.end
                                                             end:0
                                                           width:chunk.frame.size.width
                                                       lineCount:2
                                                       lineLimit:chunk.lineLimit - (chunk.lineCount - 1)] autorelease];
    CGPoint topLeft = chunk.topLeft;
    topLeft.y += (chunk.lineCount - 1) * chunk.lineHeight;
    newlineChunk.topLeft = topLeft;
    return newlineChunk;
}

- (void)drawRect:(CGRect)rect {
    //Nothing
}

- (void)offset:(CGPoint)offset {
    CGPoint cur = self.topLeft;
    cur.x += offset.x;
    cur.y += offset.y;
    self.topLeft = cur;
}

- (CGPoint)topLeft {
    return self.frame.origin;
}

- (CGPoint)topRight {
    return CGPointMake(self.frame.size.width + self.frame.origin.x, self.frame.origin.y);
}

- (CGPoint)bottomLeft {
    return CGPointMake(self.frame.origin.x, self.frame.origin.y + self.frame.size.height);
}

- (CGPoint)bottomRight {
    return CGPointMake(self.frame.origin.x + self.frame.size.width, self.frame.origin.y + self.frame.size.height);
}

- (void)_adjustOrigin:(CGPoint)cur next:(CGPoint)next {
    _frame = CGRectOffset(_frame, next.x - cur.x, next.y - cur.y);
}

- (void)setTopLeft:(CGPoint)topLeft {
    [self _adjustOrigin:self.topLeft next:topLeft];
}

- (void)setTopRight:(CGPoint)topRight {
    [self _adjustOrigin:self.topRight next:topRight];
}

- (void)setBottomLeft:(CGPoint)bottomLeft {
    [self _adjustOrigin:self.bottomLeft next:bottomLeft];
}

- (void)setBottomRight:(CGPoint)bottomRight {
    [self _adjustOrigin:self.bottomRight next:bottomRight];
}


@end
