//
//  STChunk.h
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STChunk : NSObject

- (id)initWithLineHeight:(CGFloat)lineHeight 
                   start:(CGFloat)start 
                     end:(CGFloat)end
                   width:(CGFloat)width 
               lineCount:(NSInteger)lineCount 
               lineLimit:(NSInteger)limit;

- (void)drawRect:(CGRect)rect;
- (void)offset:(CGPoint)offset;

+ (STChunk*)chunkWithLineHeight:(CGFloat)lineHeight andWidth:(CGFloat)width;
+ (STChunk*)newlineChunkWithPrev:(STChunk*)chunk;

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

@end
