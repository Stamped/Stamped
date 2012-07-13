//
//  WrappingTextView.m
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "WrappingTextView.h"
#import "UIColor+Stamped.h"

@interface WrappingTextView () 

- (CGMutablePathRef)copyPath;
- (CGRect)resizeBottomRect:(CGRect)bottomRect topRect:(CGRect)topRect;
- (NSAttributedString*)attributedStringForText;
  
@end

@implementation WrappingTextView

@synthesize previewRectSize = previewRectSize_;
@synthesize text = text_;

- (id)initWithFrame:(CGRect)aRect text:(NSString*)newText {
  self = [super initWithFrame:aRect];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
    text_ = newText;
  }
  return self;
}

- (void)dealloc {
  CFRelease(textPath_);
  [super dealloc];
}

- (CGMutablePathRef)copyPath {
  // Drawing origin is at bottom left.
  CGMutablePathRef path = CGPathCreateMutable();
  CGRect topRect = CGRectMake(0, self.frame.size.height - self.previewRectSize.height,
                              self.previewRectSize.width, self.previewRectSize.height);
  CGRect botRect = CGRectMake(0, 0, 
                              self.frame.size.width, self.frame.size.height - self.previewRectSize.height);
  botRect = [self resizeBottomRect:botRect topRect:topRect];
  
  topRect = CGRectMake(0, self.frame.size.height - self.previewRectSize.height,
                       self.previewRectSize.width, self.previewRectSize.height);

  // Draw the path clockwise starting from upper left.
  CGPathMoveToPoint(path, NULL, CGRectGetMinX(botRect), CGRectGetMaxY(topRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMaxX(topRect), CGRectGetMaxY(topRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMaxX(topRect), CGRectGetMaxY(botRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMaxX(botRect), CGRectGetMaxY(botRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMaxX(botRect), CGRectGetMinY(botRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMinX(botRect), CGRectGetMinY(botRect));
  CGPathAddLineToPoint(path, NULL, CGRectGetMinX(botRect), CGRectGetMaxY(topRect));
  CGPathCloseSubpath(path);

  return path;
}

- (CGRect)resizeBottomRect:(CGRect)botRect topRect:(CGRect)topRect {
  CGMutablePathRef path = CGPathCreateMutable();
  CGPathAddRect(path, NULL, topRect);

  NSAttributedString* string = [self attributedStringForText];

  // Determine how much of the string fits in the top rect.
  CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string);  
  CTFrameRef topFrame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, string.length), path, NULL);
  CFRange topRectRange = CTFrameGetVisibleStringRange(topFrame);
  CFRelease(topFrame);
  
  // Use topRectRange to determine how big the bottom rect needs to be to fit the rest of the text.
  CGPathRelease(path);
  CFRange fitRange;
  CFRange botRange = CFRangeMake(topRectRange.length, 0);

  CGSize suggestedSize = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, 
                                                                      botRange,
                                                                      NULL,
                                                                      CGSizeMake(botRect.size.width, CGFLOAT_MAX),
                                                                      &fitRange);
  CFRelease(framesetter);

  CGRect resizedBottomRect = botRect;
  resizedBottomRect.size.height = ceilf(suggestedSize.height);

  CGFloat newHeight = topRect.size.height + resizedBottomRect.size.height;
  CGRect newFrame = self.frame;
  newFrame.size.height = newHeight;
  self.frame = newFrame;

  return resizedBottomRect;
}

- (NSAttributedString*)attributedStringForText {
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:self.text];
  
	CTFontRef helvetica = CTFontCreateWithName(CFSTR("Helvetica"), 12.0, NULL);
  
	[string addAttribute:(id)kCTFontAttributeName
                 value:(id)helvetica
                 range:NSMakeRange(0, [string length])];

  CFRelease(helvetica);

  [string addAttribute:(id)kCTForegroundColorAttributeName
                 value:(id)[UIColor stampedGrayColor].CGColor
                 range:NSMakeRange(0, [string length])];
  
  return [string autorelease];
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  // Flip the coordinate system for right-reading text.
  CGContextSetTextMatrix(ctx, CGAffineTransformIdentity);
	CGContextTranslateCTM(ctx, 0, self.bounds.size.height);
	CGContextScaleCTM(ctx, 1.0, -1.0);

  // Create a framesetter and resize the frame to fit the text.
  NSAttributedString* string = [self attributedStringForText];
  CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string);  

  // Finally, draw.
  CTFrameRef theFrame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, string.length), textPath_, NULL);     
  CTFrameDraw(theFrame, ctx);
  
  CFRelease(framesetter); 
  CFRelease(theFrame);
}

- (void)setPreviewRectSize:(CGSize)newSize {
  previewRectSize_ = newSize;
  CGPathRef path = [self copyPath];
  textPath_ = path;
}

@end
