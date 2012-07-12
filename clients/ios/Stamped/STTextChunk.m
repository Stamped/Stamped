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

+ (NSString*)firstWord:(NSString*)string {
    NSArray* comps = [string componentsSeparatedByString:@" "];
    NSLog(@"comps:%@", comps);
    if (comps.count) {
        return [comps objectAtIndex:0];
    }
    else {
        return string;
    }
}

- (id)initWithPrev:(STChunk *)chunk text:(NSString *)text font:(UIFont *)font color:(UIColor *)color {
    return [self initWithPrev:chunk text:text font:font color:color kerning:0.0];
}

- (id)initWithPrev:(STChunk*)chunk text:(NSString*)text font:(UIFont*)font color:(UIColor*)color kerning:(CGFloat)kerning {
    if (!chunk) {
        chunk = [[[STChunk alloc] initWithLineHeight:font.ascender + font.leading start:0 end:0 width:CGFLOAT_MAX lineCount:1 lineLimit:1] autorelease];
    }
    CGFloat end;
    NSInteger lineCount;
    NSInteger lineLimit = chunk.lineLimit - (chunk.lineCount - 1);
    //TODO add fix
//    BOOL goToNextLine = NO;
//    NSString* firstWord = [STTextChunk firstWord:text];
//    if (firstWord.length) {
//        CGSize firstWordSize = [firstWord sizeWithFont:font];
//        if (firstWordSize.width >= chunk.frame.size.width - chunk.end) {
//            goToNextLine = YES;
//        }
//    }
    NSAttributedString* string = [Util attributedStringForString:text font:font color:color lineHeight:chunk.lineHeight indent:chunk.end kerning:kerning];
    CGSize size = [Util sizeForString:string thatFits:CGSizeMake(chunk.frame.size.width, chunk.lineHeight * lineLimit)];
    lineCount = roundf(size.height / chunk.lineHeight);
    //size.width = chunk.frame.size.width;
    if (lineCount == 1) {
        end = size.width + chunk.end;
    }
    else {
        size.width = chunk.frame.size.width;
        end = [Util endForString:string withSize:size];
    }
    self = [super initWithLineHeight:chunk.lineHeight start:chunk.end end:end width:chunk.frame.size.width lineCount:lineCount lineLimit:lineLimit];
    if (self) {
        self.topLeft = CGPointMake(chunk.topLeft.x, chunk.topLeft.y + chunk.lineHeight *(chunk.lineCount - 1 ) );
        _string = [string retain];
        _font = [font retain];
    }
    return self;
}

- (id)initWithPrev:(STChunk*)chunk attributedString:(NSAttributedString*)string andPrimaryFont:(UIFont*)primaryFont {
    CGFloat end;
    NSInteger lineCount;
    NSInteger lineLimit = chunk.lineLimit - (chunk.lineCount - 1);
    CGSize size = [Util sizeForString:string thatFits:CGSizeMake(chunk.frame.size.width, chunk.lineHeight * lineLimit)];
    lineCount = roundf(size.height / chunk.lineHeight);
    //size.width = chunk.frame.size.width;
    if (lineCount == 1) {
        end = size.width + chunk.end;
    }
    else {
        size.width = chunk.frame.size.width;
        end = [Util endForString:string withSize:size];
    }
    self = [super initWithLineHeight:chunk.lineHeight start:chunk.end end:end width:chunk.frame.size.width lineCount:lineCount lineLimit:lineLimit];
    if (self) {
        self.topLeft = CGPointMake(chunk.topLeft.x, chunk.topLeft.y + chunk.lineHeight *(chunk.lineCount - 1 ) );
        _string = [string retain];
        _font = [primaryFont retain];
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
