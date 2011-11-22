//
//  StampDetailHeaderView.m
//  Stamped
//
//  Created by Jake Zien on 11/21/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "StampDetailHeaderView.h"
#import "Util.h"
#import "Entity.h"
#import "UIColor+Stamped.h"
#import <CoreText/CoreText.h>

@interface StampDetailHeaderView ()

@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, retain) UIImage* stampImageInverted;
@property (nonatomic, assign) CGRect stampFrame;
@property (nonatomic, retain) NSAttributedString* titleAttrString;
@property (nonatomic, retain) NSAttributedString* titleAttrStringInverted;
@property (nonatomic, retain) CATextLayer* titleLayer;
@property (nonatomic, retain) CAGradientLayer* gradientLayer;
@property (nonatomic, assign) CGGradientRef gradientRef;
@property (nonatomic, retain) UILabel* subtitleLabel;
@property (nonatomic, retain) UIImageView* categoryImageView;
@property (nonatomic, retain) CALayer* stampLayer;
@property (nonatomic, retain) CALayer* arrowLayer;

@end


@implementation StampDetailHeaderView

@synthesize inverted = inverted_;
@synthesize stamp = stamp_;
@synthesize stampImage = stampImage_;
@synthesize stampImageInverted = stampImageInverted_;
@synthesize stampFrame = stampFrame_;
@synthesize titleAttrString = titleAttrString_;
@synthesize titleAttrStringInverted = titleAttrStringInverted_;
@synthesize title = title_;
@synthesize titleLayer = titleLayer_;
@synthesize gradientRef = gradientRef_;
@synthesize subtitleLabel = subtitleLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize gradientLayer = gradientLayer_;
@synthesize stampLayer = stampLayer_;
@synthesize delegate = delegate_;
@synthesize arrowLayer = arrowLayer_;


- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    inverted_ = NO;
    self.backgroundColor = [UIColor clearColor];
    CGColorRef color1 = [UIColor colorWithRed:0.02 green:0.55 blue:0.96 alpha:1.0].CGColor;
    CGColorRef color2 = [UIColor colorWithRed:0.0  green:0.37 blue:0.91 alpha:1.0].CGColor;
    CGFloat locations[] = {0, 1};
    self.gradientRef = CGGradientRetain(CGGradientCreateWithColors(CGColorSpaceCreateDeviceRGB(), 
                                                                   (CFArrayRef)[NSArray arrayWithObjects:(id)color1, (id)color2, nil], 
                                                                   locations));
    self.gradientLayer = [CAGradientLayer layer];
    gradientLayer_.colors = [NSArray arrayWithObjects:(id)color1, (id)color2, nil];
    gradientLayer_.frame = self.bounds;
    gradientLayer_.hidden = YES;
    
    titleLayer_ = [[CATextLayer alloc] init];
    titleLayer_.truncationMode = kCATruncationEnd;
    titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
    titleLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
    titleLayer_.font = CTFontCreateWithName((CFStringRef)@"TitlingGothicFBComp-Regular", 0, NULL);  // So the ellipsis draws the way we like it.
    titleLayer_.fontSize = 24;
    titleLayer_.hidden = YES;
    
    CGFloat ascender = CTFontGetAscent(titleLayer_.font);
    CGRect frame = CGRectMake(15, 7, 270, 56);
    frame.origin.y += ascender;
    titleLayer_.frame = frame;
    NSDictionary *newActions = [[NSDictionary alloc] initWithObjectsAndKeys:[NSNull null], @"contents", nil];
    titleLayer_.actions = newActions;
    [newActions release];
    
    categoryImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(17, 50, 15, 12)];
    categoryImageView_.contentMode = UIViewContentModeLeft;
    categoryImageView_.backgroundColor = [UIColor clearColor];
    
    subtitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 49, 270, 15)];
    subtitleLabel_.backgroundColor = [UIColor clearColor];
    subtitleLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
    subtitleLabel_.textColor = [UIColor stampedGrayColor];
    subtitleLabel_.highlightedTextColor = [UIColor whiteColor];
    
    self.arrowLayer = [CALayer layer];
    [arrowLayer_ setContents:(id)[UIImage imageNamed:@"gray_disclosure_arrow"].CGImage];
    [arrowLayer_ setFrame:CGRectMake(287, 25, 23, 23)];
    
    [self.layer addSublayer:gradientLayer_];
    [self.layer addSublayer:titleLayer_];
    [self.layer addSublayer:arrowLayer_];
    [self addSubview:categoryImageView_];
    [self addSubview:subtitleLabel_];
  }
  return self;
}

- (void)dealloc {
  self.title = nil;
  self.stamp = nil;
  self.stampImage = nil;
  self.stampImageInverted = nil;
  self.titleAttrString = nil;
  self.titleAttrStringInverted = nil;
  self.titleLayer = nil;
  CGGradientRelease(gradientRef_);
  self.gradientRef = nil;
  self.subtitleLabel = nil;
  self.categoryImageView = nil;
  self.gradientLayer = nil;
  self.delegate = nil;
  self.arrowLayer = nil;
}

- (void)setStamp:(Stamp *)stamp {
  stamp_ = stamp;
  self.stampImage = [Util stampImageForUser:stamp_.user];
  self.stampImageInverted = [Util stampImageWithPrimaryColor:@"ffffff" secondary:@"ffffff"];
  self.title = stamp.entityObject.title;
  [self setNeedsDisplay];
  
  categoryImageView_.image = stamp_.entityObject.categoryImage;
  categoryImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:stamp_.entityObject.categoryImage];
  [categoryImageView_  sizeToFit];
  CGRect frame = categoryImageView_.frame;
  frame.origin.x = titleLayer_.frame.origin.x + 1;
  categoryImageView_.frame = frame;
  subtitleLabel_.text = stamp_.entityObject.subtitle;
  frame = subtitleLabel_.frame;
  frame.origin.x = categoryImageView_.frame.origin.x + categoryImageView_.frame.size.width + 8;
  subtitleLabel_.frame = frame;
}

- (void)setTitle:(NSString *)title {
  title_ = title;
  // Create title label.  
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  
  
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTFontRef titleFont = CTFontCreateWithName((CFStringRef)fontString, fontSize, NULL);
  CTParagraphStyleRef titleStyle = CTParagraphStyleCreate(settings, numSettings);
  NSMutableDictionary* titleAttributes = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
                                          (id)titleFont, (id)kCTFontAttributeName,
                                          (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                                          (id)titleStyle, (id)kCTParagraphStyleAttributeName, nil];
  
  [titleAttributes setObject:(id)[UIColor stampedDarkGrayColor].CGColor forKey:(id)kCTForegroundColorAttributeName];
  titleAttrString_ = [[NSAttributedString alloc] initWithString:stamp_.entityObject.title attributes:titleAttributes];
  
  [titleAttributes setObject:(id)[UIColor whiteColor].CGColor forKey:(id)kCTForegroundColorAttributeName];
  titleAttrStringInverted_ = [[NSAttributedString alloc] initWithString:stamp_.entityObject.title attributes:titleAttributes];
  
  self.titleLayer.string = self.titleAttrString;
  
  
  CTFontRef ellipsisFont = CTFontCreateWithName((CFStringRef)fontString, 24, NULL);
  NSMutableDictionary* ellipsisAttributes = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
                                             (id)ellipsisFont, (id)kCTFontAttributeName,
                                             (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                                             (id)titleStyle, (id)kCTParagraphStyleAttributeName, nil];
  
  CTLineRef ellipsisLine = CTLineCreateWithAttributedString((CFAttributedStringRef)[[NSAttributedString alloc] initWithString:@"…" 
                                                                                                                   attributes:ellipsisAttributes]);
  
  CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)self.titleAttrString);
  CTLineRef truncatedLine = CTLineCreateTruncatedLine(line, 270, kCTLineTruncationEnd, ellipsisLine);
  
  CFIndex lineGlyphCount = CTLineGetGlyphCount(line);
  CFIndex truncatedLineGlyphCount = CTLineGetGlyphCount(truncatedLine);
  CFIndex lastCharIndex = (truncatedLineGlyphCount < lineGlyphCount) ? truncatedLineGlyphCount - 1 : lineGlyphCount;
  CGFloat offset = CTLineGetOffsetForStringIndex(line, lastCharIndex, nil);
  CGFloat width = fmin(270, offset);
  
  // Subtitle.
  CFRelease(line);
  CFRelease(truncatedLine);
  CFRelease(titleFont);
  CFRelease(titleStyle);
  [titleAttributes release];
  CFRelease(ellipsisFont);
  [ellipsisAttributes release];
  CFRelease(ellipsisLine);
  
  // Badge stamp.
  stampFrame_ = CGRectMake(15 + width - (46 / 2), 17 - (46 / 2), 46, 46);
  [self setNeedsDisplay];
}

- (void)drawRect:(CGRect)rect
{
  if (!stamp_ || !title_) return;
  
  if (inverted_) {
    CGPoint top = CGPointMake(160, 0);
    CGPoint bottom = CGPointMake(160, self.bounds.size.height);
    
    CGContextDrawLinearGradient(UIGraphicsGetCurrentContext(), gradientRef_, top, bottom, 0);
    
    [CATransaction begin];
    [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
      [titleLayer_ setString:titleAttrStringInverted_];
      titleLayer_.foregroundColor = [UIColor whiteColor].CGColor;
      arrowLayer_.contents = (id)[UIImage imageNamed:@"gray_disclosure_arrow_highlighted"].CGImage;
      categoryImageView_.highlighted = YES;
      subtitleLabel_.highlighted = YES;
    [CATransaction commit];
    
    CGContextSaveGState(UIGraphicsGetCurrentContext());
    CGContextTranslateCTM(UIGraphicsGetCurrentContext(), titleLayer_.frame.origin.x, titleLayer_.frame.origin.y);
    [titleLayer_ drawInContext:UIGraphicsGetCurrentContext()];
    CGContextRestoreGState(UIGraphicsGetCurrentContext());
    [stampImageInverted_ drawInRect:stampFrame_];
  }
  else {
    [CATransaction begin];
    [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
      [titleLayer_ setString:titleAttrString_];
      titleLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
      arrowLayer_.contents = (id)[UIImage imageNamed:@"gray_disclosure_arrow"].CGImage;
      categoryImageView_.highlighted = NO;
      subtitleLabel_.highlighted = NO;
    [CATransaction commit];
    
    CGContextSaveGState(UIGraphicsGetCurrentContext());
    CGContextTranslateCTM(UIGraphicsGetCurrentContext(), titleLayer_.frame.origin.x, titleLayer_.frame.origin.y);
    [titleLayer_ drawInContext:UIGraphicsGetCurrentContext()];
    CGContextRestoreGState(UIGraphicsGetCurrentContext());
    [stampImage_ drawInRect:stampFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
  }
}

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {  
  inverted_ = YES;
  [self setNeedsDisplay];
}

- (void)touchesCancelled:(NSSet *)touches withEvent:(UIEvent *)event {  
  inverted_ = NO;
  [self setNeedsDisplay];
}

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {  
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.frame, [touch locationInView:self])) {
    inverted_ = YES;
    [delegate_ handleEntityTap:self];
  }
  else
    inverted_ = NO;
  [self setNeedsDisplay];
}

- (void)touchesMoved:(NSSet *)touches withEvent:(UIEvent *)event {
}

@end
