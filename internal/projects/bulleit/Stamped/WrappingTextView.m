//
//  WrappingTextView.m
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "WrappingTextView.h"
#import "UIColor+Stamped.h"

@interface WrappingTextView () 

//- (CFArrayRef)createFrames;
//- (CFArrayRef)sizeFrames:(CFMutableArrayRef)framePaths;

- (CGPathRef)createPath;
- (CGRect)resizeBottomRect:(CGRect)bottomRect topRect:(CGRect)topRect;
- (NSAttributedString*)attributedStringForText;
  
@end



@implementation WrappingTextView

@synthesize previewRectSize = previewRectSize_;
@synthesize text = text_;

- (id)initWithFrame:(CGRect)aRect text:(NSString*)newText
{
    self = [super initWithFrame:aRect];
    if (self) {
      previewRectSize_ = CGSizeMake(0, 0);
      frameCount = 1;
      self.backgroundColor = [UIColor clearColor];
//      self.clipsToBounds = NO;
      contentHeight = 0.f;
      text_ = newText;
    }
    
    return self;
}

- (void)dealloc {
  CFRelease(textPath_);
  [super dealloc];
}


- (CGPathRef)createPath {
  
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
  CGPathMoveToPoint   (path, NULL, CGRectGetMinX(botRect), CGRectGetMaxY(topRect));
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
  CTFrameRef  topFrame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, string.length), path, NULL);
  CFRange topRectRange = CTFrameGetVisibleStringRange(topFrame);
  
  // Use topRectRange to determine how big the bottom rect needs to be to fit the rest of the text.
  CGPathRelease(path);
  path = CGPathCreateMutable();
//  CGRect stretchedBotRect = botRect;
//  stretchedBotRect.size.height = 10000;
  
//  CGPathAddRect(path, NULL, stretchedBotRect);
  CFRange fitRange;
  CFRange botRange = CFRangeMake(topRectRange.length, 0);
  
//  CTFrameRef  botFrame = CTFramesetterCreateFrame(framesetter, botRange, path, NULL);
//  CGRect  botFrameSize = CGPathGetBoundingBox( CTFrameGetPath(botFrame) );
  CGSize suggestedSize = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, 
                                                                      botRange,
                                                                      nil,
                                                                      CGSizeMake(botRect.size.width, HUGE_VAL),
                                                                      &fitRange);
  
  CGRect resizedBottomRect = botRect;
  resizedBottomRect.size.height = ceilf(suggestedSize.height);
  
  CGFloat newHeight = topRect.size.height + resizedBottomRect.size.height;
  CGRect  newFrame  = self.frame;
  newFrame.size.height = newHeight;
  self.frame = newFrame;
  
    
//  NSLog(@"botFrameSize: %f %f", botFrameSize.size.width, botFrameSize.size.height);
  NSLog(@"suggestedSize: %f %f", suggestedSize.width, suggestedSize.height);
//  NSLog(@"topRectRange: %ld %ld", topRectRange.location, topRectRange.length);
//  NSLog(@"botRange: %ld %ld", botRange.location, botRange.length);
  
  return resizedBottomRect;
}


- (NSAttributedString*)attributedStringForText {

  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:self.text];
  
	CTFontRef helvetica = CTFontCreateWithName(CFSTR("Helvetica"), 12.0, NULL);
  
	[string addAttribute:(id)kCTFontAttributeName
                 value:(id)helvetica
                 range:NSMakeRange(0, [string length])];
  
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
  
//  CGContextSetFillColorWithColor(ctx, [UIColor stampedDarkGrayColor].CGColor);
//  CGContextAddPath(ctx, path);
//  CGContextFillPath(ctx);

  // Create a mutable string with the right font, size, and color.
  
  // Create a framesetter and resize the frame to fit the text.
  NSAttributedString* string = [self attributedStringForText]; 
  
  CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string);  
  
  
  
  // Finally, draw.
  CTFrameRef theFrame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, string.length), textPath_, NULL);     
  CTFrameDraw(theFrame, ctx); 
  
  CFRelease(framesetter); 
  CFRelease(theFrame); 
}


- (void)setPreviewRectSize:(CGSize)newSize
{
  previewRectSize_ = newSize;
  CGPathRef path = [self createPath];
  textPath_ = path;
}

/*
- (CFArrayRef)createFrames {
//  CGRect bounds = CGRectMake(0, 0, self.frame.size.width, _columnHeight);

  CGRect* frameRects = (CGRect*)calloc(frameCount, sizeof(*frameRects));
  
  // Calculate height of top and bottom frames


   
//  if (self.previewRectSize.width == 0.f || self.previewRectSize.height == 0.f) {
//    frameRects[0] = CGRectMake(0, 0, self.frame.size.width, 9999);
//    frameCount = 1;
//  }
//  else {
    frameRects[0] = CGRectMake(0, -self.previewRectSize.height, self.previewRectSize.width, self.previewRectSize.height*2);
    frameRects[1] = CGRectMake(0, 12, self.frame.size.width, 100);
//  }

  // Create an array of layout paths, one for each column.
  int frame;
  
  CFMutableArrayRef array = CFArrayCreateMutable(kCFAllocatorDefault, frameCount, &kCFTypeArrayCallBacks);
  for (frame = 0; frame < frameCount; frame++) {
    CGMutablePathRef path = CGPathCreateMutable();
    CGPathAddRect(path, NULL, frameRects[frame]);
    CFArrayInsertValueAtIndex(array, frame, path);
    CFRelease(path);
  }
  
  free(frameRects);
  
  
  return [self sizeFrames:array];
}

- (CFArrayRef) sizeFrames:(CFMutableArrayRef)framePaths {
  
//  CGContextRef context = (CGContextRef)UIGraphicsGetCurrentContext();
  
//  CGContextTranslateCTM(context, 0, self.previewRectSize.height);
//  CGContextScaleCTM(context, 1.0, -1.0);
  
  [UIBezierPath bezierPathWithRect:[self bounds]];
  
  // Set up a mutable string with the correct font, color, etc.
  NSMutableAttributedString* mutableString = [[NSMutableAttributedString alloc] initWithString:self.text];
  CTFontRef helvetica = CTFontCreateWithName(CFSTR("Helvetica"), 12.0, NULL);
  [mutableString addAttribute:(id)kCTFontAttributeName 
                        value:(id)helvetica 
                        range:NSMakeRange(0, mutableString.length)];
  [mutableString addAttribute:(id)kCTForegroundColorAttributeName 
                        value:(id)[UIColor stampedGrayColor].CGColor
                        range:NSMakeRange(0, mutableString.length)];
  
  CFStringRef string = (CFStringRef) mutableString;
  
  
  CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)mutableString);
  
  // Determine how much of the text fits in the first view.
  CGPathRef path = (CGPathRef)CFArrayGetValueAtIndex(framePaths, 0);
  CTFrameRef frameRef = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, CFStringGetLength(string)), path, NULL);
  CFRange frameRange = CTFrameGetVisibleStringRange(frameRef);
  CFRange range;
    
  CGSize topViewSize = CTFramesetterSuggestFrameSizeWithConstraints (framesetter, frameRange, nil, CGSizeMake(self.previewRectSize.width, HUGE_VAL), &range);
    
  CGSize bottomViewSize = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(frameRange.length, CFStringGetLength(string)), nil, CGSizeMake(self.frame.size.width, HUGE_VAL), &range);
    
    
  CGRect* frameRects = (CGRect*)calloc(frameCount, sizeof(*frameRects));
//  frameRects[0] = CGRectMake(0, -topViewSize.height, topViewSize.width, topViewSize.height);
//  frameRects[1] = CGRectMake(0, CGRectGetMaxY(frameRects[0]), bottomViewSize.width, bottomViewSize.height);    

  frameRects[0] = CGRectMake(0, 0, topViewSize.width, topViewSize.height);
  frameRects[1] = CGRectMake(0, CGRectGetMaxY(frameRects[0]), bottomViewSize.width, bottomViewSize.height);    

  
  
  CGFloat height = frameRects[0].size.height + frameRects[1].size.height;
  contentHeight = height;
  
  CGRect newframe = self.frame;
  newframe.size.height = contentHeight;
  self.frame = newframe;
  
  NSLog(@"height %f %f", topViewSize.height,  bottomViewSize.height);
  
    
  int frame;
    
  CFMutableArrayRef array = CFArrayCreateMutable(kCFAllocatorDefault, frameCount, &kCFTypeArrayCallBacks);
  for (frame = 0; frame < frameCount; frame++) {
    CGMutablePathRef path = CGPathCreateMutable();
    CGPathAddRect(path, NULL, frameRects[frame]);
    CFArrayInsertValueAtIndex(array, frame, path);
    CFRelease(path);
  }
    
  free(frameRects);
  CFRelease(frameRef);   
  CFRelease(framePaths);
  
  return array;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef context = (CGContextRef)UIGraphicsGetCurrentContext();
  

  
  [UIBezierPath bezierPathWithRect:[self bounds]];
  
  // Set up a mutable string with the correct font, color, etc.
  NSMutableAttributedString* mutableString = [[NSMutableAttributedString alloc] initWithString:self.text];
  CTFontRef helvetica = CTFontCreateWithName(CFSTR("Helvetica"), 12.0, NULL);
  [mutableString addAttribute:(id)kCTFontAttributeName 
                        value:(id)helvetica 
                        range:NSMakeRange(0, mutableString.length)];
  [mutableString addAttribute:(id)kCTForegroundColorAttributeName 
                        value:(id)[UIColor stampedGrayColor].CGColor
                        range:NSMakeRange(0, mutableString.length)];
    
  CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)mutableString);
  
  CFArrayRef framePaths = [self createFrames];
  CFIndex pathCount = CFArrayGetCount(framePaths);
  
  CFIndex startIndex = 0;
  
  // flip the coordinate system
  CGContextTranslateCTM(context, 0, contentHeight);
  CGContextScaleCTM(context, 1.0, -1.0);
  
  
  int frame;
  for (frame = 0; frame < pathCount; frame++) {
    
    CGPathRef path = (CGPathRef)CFArrayGetValueAtIndex(framePaths, frame);
    

    // Create a frame for this column and draw it.
    CTFrameRef frameRef = CTFramesetterCreateFrame(framesetter, CFRangeMake(startIndex, 0), path, NULL);
    CTFrameDraw(frameRef, context);
    
    // Start the next frame at the first character not visible in this frame.
    CFRange frameRange = CTFrameGetVisibleStringRange(frameRef);
    startIndex += frameRange.length;
    CFRelease(frameRef);
  }
  CFRelease(framePaths);
}
*/


@end
