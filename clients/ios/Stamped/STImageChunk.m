//
//  STImageChunk.m
//  Stamped
//
//  Created by Landon Judkins on 6/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STImageChunk.h"

@interface STImageChunk ()

@property (nonatomic, readonly, assign) CGRect imageFrame;

@end

@implementation STImageChunk

@synthesize image = _image;
@synthesize imageFrame = _imageFrame;

- (id)initWithPrev:(STChunk*)chunk andFrame:(CGRect)frame {
    CGFloat width = CGRectGetMaxX(frame);
    CGFloat end;
    NSInteger lineCount;
    NSInteger lineLimit = chunk.lineLimit - (chunk.lineCount - 1);
    if (chunk.frame.size.width - chunk.end < width) {
        //Next line
        end = width;
        lineCount = 2;
    }
    else {
        //Same line
        end = chunk.end + width;
        lineCount = 1;
    }
    self = [super initWithLineHeight:chunk.lineHeight start:chunk.end end:end width:chunk.frame.size.width lineCount:lineCount lineLimit:lineLimit];
    if (self) {
        self.topLeft = CGPointMake(chunk.topLeft.x, chunk.topLeft.y + chunk.lineHeight * (chunk.lineCount - 1 ) );
        _imageFrame = frame;
    }
    return self;
}

- (void)dealloc
{
    [_image release];
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    CGContextRef context = UIGraphicsGetCurrentContext();
    CGContextSaveGState(context);
    CGContextTranslateCTM(context, self.frame.origin.x + self.start, self.frame.origin.y + self.lineHeight - self.imageFrame.size.height);
    [self.image drawInRect:self.imageFrame];
    CGContextRestoreGState(context);
}

@end
