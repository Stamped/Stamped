//
//  StampDetailHeaderView.m
//  Stamped
//
//  Created by Jake Zien on 11/21/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <CoreText/CoreText.h>

#import "StampDetailHeaderView.h"

#import "Stamp.h"
#import "Entity.h"
#import "Util.h"
#import "UIColor+Stamped.h"

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
@synthesize delegate = delegate_;
@synthesize arrowLayer = arrowLayer_;
@synthesize hideArrow = hideArrow_;


- (id)initWithFrame:(CGRect)aFrame {
  self = [super initWithFrame:aFrame];
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
    
    CGFloat ascender = ceilf(CTFontGetAscent(titleLayer_.font)) + 1;
    CGRect frame = CGRectMake(15, ascender, aFrame.size.width - 50, 56);

    titleLayer_.frame = frame;
    NSDictionary *newActions = [[NSDictionary alloc] initWithObjectsAndKeys:[NSNull null], @"contents", nil];
    titleLayer_.actions = newActions;
    [newActions release];
    
    categoryImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(15, 45, 15, 12)];
    categoryImageView_.contentMode = UIViewContentModeLeft;
    categoryImageView_.backgroundColor = [UIColor clearColor];
    
    subtitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 44, aFrame.size.width - 50, 15)];
    subtitleLabel_.backgroundColor = [UIColor clearColor];
    subtitleLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
    subtitleLabel_.textColor = [UIColor stampedGrayColor];
    subtitleLabel_.highlightedTextColor = [UIColor whiteColor];
    
    self.arrowLayer = [CALayer layer];
    [arrowLayer_ setContents:(id)[UIImage imageNamed:@"gray_disclosure_arrow"].CGImage];
    [arrowLayer_ setFrame:CGRectMake(287, 20, 23, 23)];
    
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
  [super dealloc];
}

- (void)setStamp:(Stamp*)stamp {
  if (stamp_ != stamp) {
    [stamp_ release];
    stamp_ = [stamp retain];
    if (stamp) {
      self.stampImage = [Util stampImageForUser:stamp_.user];
      self.stampImageInverted = [Util stampImageWithPrimaryColor:@"ffffff" secondary:@"ffffff"];
      self.title = stamp.entityObject.title;
      
      categoryImageView_.image = stamp_.entityObject.categoryImage;
      categoryImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:stamp_.entityObject.categoryImage];
      [categoryImageView_ sizeToFit];
      CGRect frame = categoryImageView_.frame;
      frame.origin.x = titleLayer_.frame.origin.x + 1;
      categoryImageView_.frame = frame;
      subtitleLabel_.text = stamp_.entityObject.subtitle;
      frame = subtitleLabel_.frame;
      frame.origin.x = categoryImageView_.frame.origin.x + categoryImageView_.frame.size.width + 8;
      subtitleLabel_.frame = frame;
      [self setNeedsDisplay];
    }
  }
}

// Only used in stamp creator, i.e., when there is no stamp yet.
- (void)setEntity:(Entity*)entity {
  self.stampImage = nil;
  self.stampImageInverted = nil;
  self.title = [entity valueForKey:@"title"];
  
  categoryImageView_.image = [entity valueForKey:@"categoryImage"];
  categoryImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:categoryImageView_.image];
  [categoryImageView_  sizeToFit];
  CGRect frame = categoryImageView_.frame;
  frame.origin.x = titleLayer_.frame.origin.x + 1;
  categoryImageView_.frame = frame;
  subtitleLabel_.text = [entity valueForKey:@"subtitle"];
  frame = subtitleLabel_.frame;
  frame.origin.x = categoryImageView_.frame.origin.x + categoryImageView_.frame.size.width + 8;
  subtitleLabel_.frame = frame;
  [self setNeedsDisplay];
}

- (void)setTitle:(NSString*)title {
  if (title_ != title) {
    [title_ release];
    title_ = [title copy];
    if (title) {
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
      titleAttrString_ = [[NSAttributedString alloc] initWithString:title_ attributes:titleAttributes];
      
      [titleAttributes setObject:(id)[UIColor whiteColor].CGColor forKey:(id)kCTForegroundColorAttributeName];
      titleAttrStringInverted_ = [[NSAttributedString alloc] initWithString:title_ attributes:titleAttributes];
      
      self.titleLayer.string = self.titleAttrString;
      
      
      CTFontRef ellipsisFont = CTFontCreateWithName((CFStringRef)fontString, 24, NULL);
      NSMutableDictionary* ellipsisAttributes = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
                                                 (id)ellipsisFont, (id)kCTFontAttributeName,
                                                 (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                                                 (id)titleStyle, (id)kCTParagraphStyleAttributeName, nil];
      
      CTLineRef ellipsisLine = CTLineCreateWithAttributedString((CFAttributedStringRef)[[[NSAttributedString alloc] initWithString:@"…" 
                                                                                                                       attributes:ellipsisAttributes] autorelease]);
      
      CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)self.titleAttrString);
      CTLineRef truncatedLine = CTLineCreateTruncatedLine(line, 270, kCTLineTruncationEnd, ellipsisLine);
      
      CFIndex lineGlyphCount = CTLineGetGlyphCount(line);
      CFIndex truncatedLineGlyphCount = CTLineGetGlyphCount(truncatedLine);
      CFIndex lastCharIndex = (truncatedLineGlyphCount < lineGlyphCount) ? truncatedLineGlyphCount - 1 : lineGlyphCount;
      CFIndex ligatureCt = title_.length - lineGlyphCount;
      if (ligatureCt > 0)
        lastCharIndex += ligatureCt;
      CGFloat offset = CTLineGetOffsetForStringIndex(line, lastCharIndex, nil);
      CGFloat width = fmin(self.frame.size.width - 56, offset);
      
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
      stampFrame_ = CGRectMake(22 + width - (46 / 2), 13 - (46 / 2), 46, 46);
      [self setNeedsDisplay];
    }
  }
}

- (void)drawRect:(CGRect)rect {
  if (!title_) 
    return;
  
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
  } else {
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

- (void)setHideArrow:(BOOL)hideArrow {
  hideArrow_ = hideArrow;
  if (hideArrow_)
    arrowLayer_.hidden = YES;
  else
    arrowLayer_.hidden = NO;
}


- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  if (!hideArrow_)
    inverted_ = YES;
  [self setNeedsDisplay];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {  
  inverted_ = NO;
  [self setNeedsDisplay];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {  
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.frame, [touch locationInView:self]) && !hideArrow_) {
    inverted_ = YES;
    [delegate_ handleEntityTap:self];
  } else {
    inverted_ = NO;
  }
  [self setNeedsDisplay];
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {}

- (CGRect)stampFrame {
  return stampFrame_;
}

@end
