//
//  STTextChunk.m
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTextChunk.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>

@interface STTextChunk ()

@property (nonatomic, readonly, retain) NSAttributedString* string;
@property (nonatomic, readonly, retain) UIFont* font;

@end

@implementation STTextChunk

@synthesize string = _string;
@synthesize font = _font;

- (id)initWithPrev:(STChunk *)chunk text:(NSString *)text font:(UIFont *)font color:(UIColor*)color {
    if (!chunk) {
        chunk = [[[STChunk alloc] initWithLineHeight:font.ascender + font.leading start:0 end:0 width:CGFLOAT_MAX lineCount:1 lineLimit:1] autorelease];
    }
    CGFloat end;
    NSInteger lineCount;
    NSInteger lineLimit = chunk.lineLimit - (chunk.lineCount - 1);
    NSLog(@"%d", lineLimit);
    NSAttributedString* string = [Util attributedStringForString:text font:font color:color lineHeight:chunk.lineHeight indent:chunk.end];
    CGSize size = [Util sizeForString:string thatFits:CGSizeMake(chunk.frame.size.width, chunk.lineHeight * lineLimit)];
    lineCount = roundf(size.height / chunk.lineHeight);
    end = [Util endForString:string withSize:size];
    self = [super initWithLineHeight:chunk.lineHeight start:chunk.end end:end width:chunk.frame.size.width lineCount:lineCount lineLimit:lineLimit];
    if (self) {
        self.topLeft = CGPointMake(chunk.topLeft.x, chunk.topLeft.y + chunk.lineHeight *(chunk.lineCount - 1 ) );
        _string = [string retain];
        _font = [font retain];
    }
    return self;
}

- (void)dealloc
{
    [_string release];
    [_font release];
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    CGPoint topLeft = self.topLeft;
    topLeft.y -= self.font.descender;
    [Util drawAttributedString:self.string atPoint:topLeft withWidth:self.frame.size.width andMaxHeight:self.lineLimit * self.lineHeight];
}

@end
