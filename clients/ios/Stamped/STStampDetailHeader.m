//
//  STStampDetailHeader.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailHeader.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"

@interface STStampDetailHeader ()
@property (nonatomic, retain) CATextLayer* titleLayer;

- (void)_commonInit;
@end

@implementation STStampDetailHeader

@synthesize title = _title;
@synthesize titleLayer = _titleLayer;
@synthesize arrowImageView = _arrowImageView;
@synthesize subtitleLabel = _subtitleLabel;
@synthesize categoryImageView = _categoryImageView;
@synthesize stampImage = _stampImage;

- (id)initWithFrame:(CGRect)aFrame {
  self = [super initWithFrame:aFrame];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (void)dealloc {
  [_title release];
  [_titleLayer release];
  [super dealloc];
}

#pragma mark - Private methods.

- (void)_commonInit {
  self.backgroundColor = [UIColor clearColor];
  _arrowImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"gray_disclosure_arrow"]];
  _arrowImageView.frame = CGRectOffset(_arrowImageView.frame, 287, 20);
  [self addSubview:_arrowImageView];
  [_arrowImageView release];

  _titleLayer = [[CATextLayer alloc] init];
  _titleLayer.truncationMode = kCATruncationEnd;
  _titleLayer.contentsScale = [[UIScreen mainScreen] scale];
  _titleLayer.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
  // So the ellipsis draws the way we like it.
  _titleLayer.font = CTFontCreateWithName((CFStringRef)@"TitlingGothicFBComp-Regular", 0, NULL);
  _titleLayer.fontSize = 24;
  
  _categoryImageView = [[UIImageView alloc] initWithFrame:CGRectZero];
  _categoryImageView.contentMode = UIViewContentModeLeft;
  _categoryImageView.backgroundColor = [UIColor clearColor];
  [self addSubview:_categoryImageView];
  [_categoryImageView release];
  
  _subtitleLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  _subtitleLabel.backgroundColor = [UIColor clearColor];
  _subtitleLabel.lineBreakMode = UILineBreakModeTailTruncation;
  _subtitleLabel.font = [UIFont systemFontOfSize:11];
  _subtitleLabel.textColor = [UIColor stampedGrayColor];
  _subtitleLabel.highlightedTextColor = [UIColor whiteColor];
  [self addSubview:_subtitleLabel];
  [_subtitleLabel release];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  CGFloat ascender = ceilf(CTFontGetAscent(_titleLayer.font)) + 1;
  _titleLayer.frame = CGRectMake(15, ascender, CGRectGetWidth(self.frame) - 50, 56);
  CGSize imageSize = _categoryImageView.image.size;
  _categoryImageView.frame = CGRectMake(CGRectGetMinX(_titleLayer.frame), 47, imageSize.width, imageSize.height);
  CGSize subtitleSize = [_subtitleLabel sizeThatFits:CGSizeMake(280, MAXFLOAT)];
  _subtitleLabel.frame = CGRectMake(CGRectGetMaxX(_categoryImageView.frame) + 4,
                                    CGRectGetMinY(_categoryImageView.frame) - 1,
                                    280, subtitleSize.height);
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  if (!_title)
    return;

  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTFontRef titleFont = CTFontCreateWithName((CFStringRef)fontString, fontSize, NULL);
  CTParagraphStyleRef titleStyle = CTParagraphStyleCreate(settings, numSettings);
  NSDictionary* titleAttributes = [NSDictionary dictionaryWithObjectsAndKeys:
                                   (id)titleFont, (id)kCTFontAttributeName,
                                   (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                                   (id)titleStyle, (id)kCTParagraphStyleAttributeName,
                                   (id)[NSNumber numberWithFloat:0.3], (id)kCTKernAttributeName, nil];
  NSAttributedString* attrString = [[[NSAttributedString alloc] initWithString:_title attributes:titleAttributes] autorelease];
  self.titleLayer.string = attrString;

  CTFontRef ellipsisFont = CTFontCreateWithName((CFStringRef)fontString, 24, NULL);
  NSDictionary* ellipsisAttributes = [NSDictionary dictionaryWithObjectsAndKeys:
                                      (id)ellipsisFont, (id)kCTFontAttributeName,
                                      (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                                      (id)titleStyle, (id)kCTParagraphStyleAttributeName, nil];
  
  CTLineRef ellipsisLine = CTLineCreateWithAttributedString((CFAttributedStringRef)[[[NSAttributedString alloc] initWithString:@"\u2026" 
                                                                                                                    attributes:ellipsisAttributes] autorelease]);
  
  CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)attrString);
  CTLineRef truncatedLine = CTLineCreateTruncatedLine(line, CGRectGetWidth(_titleLayer.frame), kCTLineTruncationEnd, ellipsisLine);
  
  CFIndex lineGlyphCount = CTLineGetGlyphCount(line);
  CFIndex truncatedLineGlyphCount = CTLineGetGlyphCount(truncatedLine);
  CFIndex lastCharIndex = (truncatedLineGlyphCount < lineGlyphCount) ? truncatedLineGlyphCount - 1 : lineGlyphCount;
  CFIndex ligatureCt = _title.length - lineGlyphCount;
  if (ligatureCt > 0)
    lastCharIndex += ligatureCt;
  CGFloat offset = CTLineGetOffsetForStringIndex(line, lastCharIndex, nil);
  CGFloat width = fmin(CGRectGetWidth(self.frame) - 65, offset);
  
  // Subtitle.
  CFRelease(line);
  CFRelease(truncatedLine);
  CFRelease(titleFont);
  CFRelease(titleStyle);
  CFRelease(ellipsisFont);
  CFRelease(ellipsisLine);

  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextTranslateCTM(ctx, _titleLayer.frame.origin.x, _titleLayer.frame.origin.y);
  [_titleLayer drawInContext:ctx];
  CGContextRestoreGState(ctx);
  [_stampImage drawInRect:CGRectMake(22 + width - (46 / 2), 13 - (46 / 2), _stampImage.size.width, _stampImage.size.height)
                blendMode:kCGBlendModeMultiply
                    alpha:1.0];
}

@end
