//
//  STNavigationBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STNavigationBar.h"

#import <QuartzCore/QuartzCore.h>
#import <CoreText/CoreText.h>
#import "UIColor+Stamped.h"

@interface STNavigationBar ()
- (void)initialize;
- (CGPathRef)newPathForTitle;

@property (nonatomic, readonly) CALayer* ripplesLayer;
@end

@implementation STNavigationBar

@synthesize ripplesLayer = ripplesLayer_;
@synthesize hideLogo = hideLogo_;
@synthesize string = string_;
@synthesize black = black_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];
  
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];
  
  return self;
}

- (void)dealloc {
  self.string = nil;
  ripplesLayer_ = nil;
  [super dealloc];
}

- (void)drawRect:(CGRect)rect {
  if (black_) {
    [super drawRect:rect];
    return;
  }

  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, [UIColor blackColor].CGColor);
  CGContextFillRect(ctx, rect);
  
    CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect byRoundingCorners:(UIRectCornerTopLeft | UIRectCornerTopRight) cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath);
    CGContextClip(ctx);
    
  //hideLogo_ = ![self.topItem.title isEqualToString:@"Stamps"];
  
  if (hideLogo_)
    [[UIImage imageNamed:@"nav_bar_no_logo"] drawInRect:rect];
  else
    [[UIImage imageNamed:@"nav_bar"] drawInRect:rect];
  
  if (hideLogo_) {
    CGPathRef textPath = [self newPathForTitle];
    if (!textPath)
      return;

    CGRect textPathBounds = CGPathGetBoundingBox(textPath);
    
    CGColorRef color1 = [UIColor colorWithWhite:0.90 alpha:1.0].CGColor;
//    CGColorRef     color2 = [UIColor colorWithWhite:0.85  alpha:1.0].CGColor;
//    CFArrayRef     colors = (CFArrayRef)[NSArray arrayWithObjects:(id)color1, (id)color2, nil];
//    CGFloat  locations[2] = { 0.0, 1.0 };    
//    CGGradientRef gradient = CGGradientCreateWithColors(NULL, colors, NULL);
    
  
    CGContextTranslateCTM(ctx, 
                          (self.frame.size.width - textPathBounds.size.width) / 2,
                          (self.frame.size.height - 12.0) / 2);
    CGContextAddPath(ctx, textPath);
    CGContextSetFillColorWithColor(ctx, color1);
    CGContextFillPath(ctx);

    CGContextAddPath(ctx, textPath);
    CGContextClip(ctx);

    CGContextAddPath(ctx, textPath);
    CGContextSetStrokeColorWithColor(ctx, [UIColor whiteColor].CGColor);
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0, 1.0), 2.0, [UIColor colorWithWhite:0.0 alpha:0.3].CGColor);
    CGContextSetBlendMode(ctx, kCGBlendModeMultiply);
    CGContextStrokePath(ctx);
    
    
    CGContextTranslateCTM(ctx, 
                          -(self.frame.size.width - textPathBounds.size.width) / 2,
                          -(self.frame.size.height - 10.0) / 2);
    
    
//    CGContextDrawLinearGradient(ctx, gradient,
//                                CGPointMake(self.bounds.size.width/2, 0),
//                                CGPointMake(self.bounds.size.width/2, self.bounds.size.height),
//                                0);

    CFRelease(textPath);
  }
}

- (void)initialize {
  NSLog(@"initializing navbar");
  self.layer.masksToBounds = NO;

  CGFloat ripplesY = CGRectGetMaxY(self.bounds);
  ripplesLayer_ = [[CALayer alloc] init];
  ripplesLayer_.frame = CGRectMake(0, ripplesY, 320, 3);
  ripplesLayer_.contentsGravity = kCAGravityResizeAspect;
  ripplesLayer_.contents = (id)[UIImage imageNamed:@"nav_bar_ripple"].CGImage;
  [self.layer addSublayer:ripplesLayer_];
  [ripplesLayer_ release];
}

- (void)setBlack:(BOOL)black {
  if (black == black_)
    return;

  black_ = black;
  
  ripplesLayer_.hidden = black;
  [self setNeedsDisplay];
}

- (CGPathRef)newPathForTitle {
  if (!self.topItem.title)
    return nil;

  CGContextRef ctx = UIGraphicsGetCurrentContext(); 
  
  // Flip the coordinate system for right-reading text.
  CGContextSetTextMatrix(ctx, CGAffineTransformIdentity);
	CGContextTranslateCTM(ctx, 0, self.bounds.size.height);
	CGContextScaleCTM(ctx, 1.0, -1.0);
  
  // Make an attrributed string reference from string member variable.
  CFAttributedStringRef attStr;

  UIFont* font = [UIFont fontWithName:@"Helvetica-Bold" size:20.0];
  CTFontRef ctFont = CTFontCreateWithName((CFStringRef)font.fontName, font.pointSize, NULL);
  NSDictionary* attributes = [NSDictionary dictionaryWithObjectsAndKeys:
                              (id)ctFont, kCTFontAttributeName, // NSFontAttributeName
                              (id)[NSNumber numberWithInteger:0], kCTLigatureAttributeName,
                              nil];
  NSAssert(attributes != nil, @"Font attributes are nil!");
  
  NSAttributedString* nsAttStr = [[[NSAttributedString alloc] initWithString:self.topItem.title
                                                                  attributes:attributes] autorelease];
  attStr = (CFAttributedStringRef)nsAttStr; 
  
  // Make a path from each glyph of the attributed string ref.
  CTLineRef line = CTLineCreateWithAttributedString(attStr);
  CFArrayRef runArray = CTLineGetGlyphRuns(line);
  CGMutablePathRef textPath = CGPathCreateMutable();
  
  // For each RUN...
  for (CFIndex runIndex = 0; runIndex < CFArrayGetCount(runArray); runIndex++) {
    // Get FONT for this run...
    CTRunRef run = (CTRunRef)CFArrayGetValueAtIndex(runArray, runIndex);
    CTFontRef runFont = CFDictionaryGetValue(CTRunGetAttributes(run), kCTFontAttributeName);
    
    // For each GLYPH in run...
    for (CFIndex runGlyphIndex = 0; runGlyphIndex < CTRunGetGlyphCount(run); runGlyphIndex++) {
      //  Get the glyph...
      CFRange thisGlyphRange = CFRangeMake(runGlyphIndex, 1);
      CGGlyph glyph;
      CGPoint position;
      CTRunGetGlyphs(run, thisGlyphRange, &glyph);
      CTRunGetPositions(run, thisGlyphRange, &position);
      
      // Add it to the textPath.
      //TODO MEMORY_LEAK
      CGPathRef path = CTFontCreatePathForGlyph(runFont, glyph, NULL);
      CGAffineTransform transform = CGAffineTransformMakeTranslation(position.x, position.y);
      CGPathAddPath(textPath, &transform, path);
    }
  }
  return textPath;
}

@end
