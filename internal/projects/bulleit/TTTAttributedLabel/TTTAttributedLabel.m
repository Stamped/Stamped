// TTTAttributedLabel.m
//
// Copyright (c) 2011 Mattt Thompson (http://mattt.me)
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#import "TTTAttributedLabel.h"

#include <QuartzCore/QuartzCore.h>

static inline CTTextAlignment CTTextAlignmentFromUITextAlignment(UITextAlignment alignment) {
	switch (alignment) {
		case UITextAlignmentLeft: return kCTLeftTextAlignment;
		case UITextAlignmentCenter: return kCTCenterTextAlignment;
		case UITextAlignmentRight: return kCTRightTextAlignment;
		default: return kCTNaturalTextAlignment;
	}
}

static inline CTLineBreakMode CTLineBreakModeFromUILineBreakMode(UILineBreakMode lineBreakMode) {
	switch (lineBreakMode) {
		case UILineBreakModeWordWrap: return kCTLineBreakByWordWrapping;
		case UILineBreakModeCharacterWrap: return kCTLineBreakByCharWrapping;
		case UILineBreakModeClip: return kCTLineBreakByClipping;
		case UILineBreakModeHeadTruncation: return kCTLineBreakByTruncatingHead;
		case UILineBreakModeTailTruncation: return kCTLineBreakByTruncatingTail;
		case UILineBreakModeMiddleTruncation: return kCTLineBreakByTruncatingMiddle;
		default: return 0;
	}
}

static inline NSTextCheckingType NSTextCheckingTypeFromUIDataDetectorType(UIDataDetectorTypes dataDetectorType) {
    NSTextCheckingType textCheckingType = 0;
    if (dataDetectorType & UIDataDetectorTypeAddress) {
        textCheckingType |= NSTextCheckingTypeAddress;
    }
    
    if (dataDetectorType & UIDataDetectorTypeCalendarEvent) {
        textCheckingType |= NSTextCheckingTypeDate;
    }
    
    if (dataDetectorType & UIDataDetectorTypeLink) {
        textCheckingType |= NSTextCheckingTypeLink;
    }
    
    if (dataDetectorType & UIDataDetectorTypePhoneNumber) {
        textCheckingType |= NSTextCheckingTypePhoneNumber;
    }
    
    return textCheckingType;
}

static inline NSDictionary* NSAttributedStringAttributesFromLabel(UILabel* label) {
    NSMutableDictionary *mutableAttributes = [NSMutableDictionary dictionary]; 
    
    CTFontRef font = CTFontCreateWithName((CFStringRef)label.font.fontName, label.font.pointSize, NULL);
    [mutableAttributes setObject:(id)font forKey:(NSString *)kCTFontAttributeName];
    CFRelease(font);
    
    [mutableAttributes setObject:(id)[label.textColor CGColor] forKey:(NSString*)kCTForegroundColorAttributeName];
    
    CTTextAlignment alignment = CTTextAlignmentFromUITextAlignment(label.textAlignment);
    CTLineBreakMode lineBreakMode = CTLineBreakModeFromUILineBreakMode(label.lineBreakMode);
    CTParagraphStyleSetting paragraphStyles[2] = {
		{.spec = kCTParagraphStyleSpecifierAlignment, .valueSize = sizeof(CTTextAlignment), .value = (const void*)&alignment},
		{.spec = kCTParagraphStyleSpecifierLineBreakMode, .valueSize = sizeof(CTLineBreakMode), .value = (const void*)&lineBreakMode},
	};
	CTParagraphStyleRef paragraphStyle = CTParagraphStyleCreate(paragraphStyles, 2);
	[mutableAttributes setObject:(id)paragraphStyle forKey:(NSString*)kCTParagraphStyleAttributeName];
	CFRelease(paragraphStyle);
    
  return [NSDictionary dictionaryWithDictionary:mutableAttributes];
}

@interface TTTAttributedLabel ()
@property (readwrite, nonatomic, copy) NSAttributedString* attributedText;
@property (readwrite, nonatomic, assign) CTFramesetterRef framesetter;
@property (readwrite, nonatomic, assign) CTFramesetterRef shadowFramesetter;
@property (readwrite, nonatomic, assign) CTFramesetterRef highlightFramesetter;
@property (readwrite, nonatomic, retain) NSArray* links;
@property (nonatomic, assign) NSRange selectedRange;

- (id)initCommon;
- (NSArray*)detectedLinksInString:(NSString*)string range:(NSRange)range error:(NSError**)error;
- (NSTextCheckingResult*)linkAtCharacterIndex:(CFIndex)idx;
- (NSTextCheckingResult*)linkAtPoint:(CGPoint)p;
- (NSUInteger)characterIndexAtPoint:(CGPoint)p;
- (NSRange)rangeIntersection:(NSRange)first withSecond:(NSRange)second;
- (void)drawSelectionWithRange:(NSRange)selectionRange;
- (void)clearSelection;
- (void)drawFramesetter:(CTFramesetterRef)framesetter textRange:(CFRange)textRange inRect:(CGRect)rect context:(CGContextRef)c;
@end

@implementation TTTAttributedLabel
@dynamic text;
@synthesize attributedText = _attributedText;
@synthesize framesetter = _framesetter;
@synthesize shadowFramesetter = _shadowFramesetter;
@synthesize highlightFramesetter = _highlightFramesetter;
@synthesize selectedRange = _selectedRange;

@synthesize delegate = _delegate;
@synthesize dataDetectorTypes = _dataDetectorTypes;
@synthesize links = _links;
@synthesize linkAttributes = _linkAttributes;
@synthesize verticalAlignment = _verticalAlignment;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (!self) {
    return nil;
  }
  
  return [self initCommon];
}

- (id)initWithCoder:(NSCoder *)coder {
  self = [super initWithCoder:coder];
  if (!self) {
    return nil;
  }
  
  return [self initCommon];
}

- (id)initCommon {
  self.dataDetectorTypes = UIDataDetectorTypeNone;
  self.links = [NSArray array];
  
  NSMutableDictionary *mutableLinkAttributes = [NSMutableDictionary dictionary];
  [mutableLinkAttributes setValue:(id)[[UIColor blueColor] CGColor] forKey:(NSString*)kCTForegroundColorAttributeName];
  [mutableLinkAttributes setValue:[NSNumber numberWithBool:YES] forKey:(NSString *)kCTUnderlineStyleAttributeName];
  self.linkAttributes = [NSDictionary dictionaryWithDictionary:mutableLinkAttributes];
  
  return self;
}

- (void)dealloc {
  if (_framesetter) CFRelease(_framesetter);
  if (_shadowFramesetter) CFRelease(_shadowFramesetter);
  if (_highlightFramesetter) CFRelease(_highlightFramesetter);
  
  [_attributedText release];
  [_links release];
  [_linkAttributes release];
  [super dealloc];
}

#pragma mark -

- (void)setAttributedText:(NSAttributedString*)text {
    if ([text isEqualToAttributedString:self.attributedText]) {
        return;
    }
    
    [self willChangeValueForKey:@"attributedText"];
    [_attributedText release];
    _attributedText = [text copy];
    [self didChangeValueForKey:@"attributedText"];
    
    [self setNeedsFramesetter];
}

- (void)setNeedsFramesetter {
    _needsFramesetter = YES;
}

- (CTFramesetterRef)framesetter {
    if (_needsFramesetter) {
        @synchronized(self) {
            if (_framesetter) CFRelease(_framesetter);
            if (_shadowFramesetter) CFRelease(_shadowFramesetter);
            if (_highlightFramesetter) CFRelease(_highlightFramesetter);
            
            self.framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)self.attributedText);
            self.shadowFramesetter = nil;
            self.highlightFramesetter = nil;
            _needsFramesetter = NO;
        }
    }
    
    return _framesetter;
}

- (BOOL)isUserInteractionEnabled {
    return !_userInteractionDisabled && [self.links count] > 0;
}

- (void)setUserInteractionEnabled:(BOOL)userInteractionEnabled {
    _userInteractionDisabled = !userInteractionEnabled;
}

- (BOOL)isExclusiveTouch {
    return [self.links count] > 0;
}

#pragma mark -

- (NSArray *)detectedLinksInString:(NSString *)string range:(NSRange)range error:(NSError **)error {
    if (!string) {
        return [NSArray array];
    }
    NSMutableArray *mutableLinks = [NSMutableArray array];
    NSDataDetector *dataDetector = [NSDataDetector dataDetectorWithTypes:NSTextCheckingTypeFromUIDataDetectorType(self.dataDetectorTypes) error:error];
    [dataDetector enumerateMatchesInString:string options:0 range:range usingBlock:^(NSTextCheckingResult *result, NSMatchingFlags flags, BOOL *stop) {
        [mutableLinks addObject:result];
    }];
    
    return [NSArray arrayWithArray:mutableLinks];
}

- (void)addLinkWithTextCheckingResult:(NSTextCheckingResult *)result {
    self.links = [self.links arrayByAddingObject:result];
    
    if (self.linkAttributes) {
        NSMutableAttributedString *mutableAttributedString = [[[NSMutableAttributedString alloc] initWithAttributedString:self.attributedText] autorelease];
        [mutableAttributedString addAttributes:self.linkAttributes range:result.range];
        self.attributedText = mutableAttributedString;        
    }
}

- (void)addLinkToURL:(NSURL *)url withRange:(NSRange)range {
    [self addLinkWithTextCheckingResult:[NSTextCheckingResult linkCheckingResultWithRange:range URL:url]];
}

- (void)addLinkToAddress:(NSDictionary *)addressComponents withRange:(NSRange)range {
    [self addLinkWithTextCheckingResult:[NSTextCheckingResult addressCheckingResultWithRange:range components:addressComponents]];
}

- (void)addLinkToPhoneNumber:(NSString *)phoneNumber withRange:(NSRange)range {
    [self addLinkWithTextCheckingResult:[NSTextCheckingResult phoneNumberCheckingResultWithRange:range phoneNumber:phoneNumber]];
}

- (void)addLinkToDate:(NSDate *)date withRange:(NSRange)range {
    [self addLinkWithTextCheckingResult:[NSTextCheckingResult dateCheckingResultWithRange:range date:date]];
}

- (void)addLinkToDate:(NSDate *)date timeZone:(NSTimeZone *)timeZone duration:(NSTimeInterval)duration withRange:(NSRange)range {
    [self addLinkWithTextCheckingResult:[NSTextCheckingResult dateCheckingResultWithRange:range date:date timeZone:timeZone duration:duration]];
}

#pragma mark -

- (NSTextCheckingResult *)linkAtCharacterIndex:(CFIndex)idx {
    for (NSTextCheckingResult *result in self.links) {
        NSRange range = result.range;
        if (range.location <= idx && idx <= range.location + range.length) {
            return result;
        }
    }
    
    return nil;
}

- (NSTextCheckingResult*)linkAtPoint:(CGPoint)p {
  CFIndex index = [self characterIndexAtPoint:p];
  return [self linkAtCharacterIndex:index];
}

- (NSUInteger)characterIndexAtPoint:(CGPoint)p {
  if (!CGRectContainsPoint(self.bounds, p))
    return NSNotFound;

  // Convert tap coordinates (start at top left) to CT coordinates (start at bottom left)
  p = CGPointMake(p.x, self.bounds.size.height - p.y);

  CFIndex index = NSNotFound;
  CGMutablePathRef path = CGPathCreateMutable();
  CGPathAddRect(path, NULL, self.bounds);
  CTFrameRef frame = CTFramesetterCreateFrame(self.framesetter, CFRangeMake(0, self.attributedText.length), path, NULL);
  NSArray* lines = (NSArray*)CTFrameGetLines(frame);
  CFIndex numLines = lines.count;
  CGPoint lineOrigins[numLines];
  CTFrameGetLineOrigins(frame, CFRangeMake(0, 0), lineOrigins);
  
  for (CFIndex i = 0; i < numLines; ++i) {
    CTLineRef line = (CTLineRef)[lines objectAtIndex:i];
    CGFloat ascent, descent;
    double lineWidth = CTLineGetTypographicBounds(line, &ascent, &descent, NULL);
    if (lineWidth == 0)
      return NSNotFound;

    CGPoint lineOrigin = lineOrigins[i];
    if ((p.y > (floor(lineOrigin.y) - floor(descent))) && (p.y < (ceil(lineOrigin.y) + ceil(ascent)))) {
      p.x -= lineOrigin.x;
      p.y -= lineOrigin.y;
      index = CTLineGetStringIndexForPosition(line, p);
		  break;
    }
  }
  
  CFRelease(frame);
  CFRelease(path);
      
  return index;
}

- (void)drawFramesetter:(CTFramesetterRef)framesetter textRange:(CFRange)textRange inRect:(CGRect)rect context:(CGContextRef)c {
  CGMutablePathRef path = CGPathCreateMutable();

  CGPathAddRect(path, NULL, rect);
  CTFrameRef frame = CTFramesetterCreateFrame(framesetter, textRange, path, NULL);
  CTFrameDraw(frame, c);

  CFRelease(frame);
  CFRelease(path);
}

#pragma mark - TTTAttributedLabel

- (void)setText:(id)text {
  if ([text isKindOfClass:[NSString class]]) {
    [self setText:text afterInheritingLabelAttributesAndConfiguringWithBlock:nil];
  } else {
    self.attributedText = text;
  }
  
  self.links = [NSArray array];
  if (self.dataDetectorTypes != UIDataDetectorTypeNone) {
    for (NSTextCheckingResult* result in [self detectedLinksInString:[self.attributedText string] range:NSMakeRange(0, [text length]) error:nil]) {
      [self addLinkWithTextCheckingResult:result];
    }
  }
  
  [super setText:[self.attributedText string]];
}

- (void)setText:(id)text afterInheritingLabelAttributesAndConfiguringWithBlock:(NSMutableAttributedString*(^)(NSMutableAttributedString* mutableAttributedString))block {
  if ([text isKindOfClass:[NSString class]]) {
    self.attributedText = [[[NSAttributedString alloc] initWithString:text] autorelease];
  }
  
  NSMutableAttributedString* mutableAttributedString = [[[NSMutableAttributedString alloc] initWithAttributedString:self.attributedText] autorelease];
  [mutableAttributedString addAttributes:NSAttributedStringAttributesFromLabel(self) range:NSMakeRange(0, mutableAttributedString.length)];

  if (block) {
    [self setText:block(mutableAttributedString)];
  } else {
    [self setText:mutableAttributedString];
  }
}

// Helper method for obtaining the intersection of two ranges (for handling
// selection range across multiple line ranges in drawRangeAsSelection below)
- (NSRange)rangeIntersection:(NSRange)first withSecond:(NSRange)second {
  NSRange result = NSMakeRange(NSNotFound, 0);
  
  // Ensure first range does not start after second range
  if (first.location > second.location) {
    NSRange tmp = first;
    first = second;
    second = tmp;
  }
  
  // Find the overlap intersection range between first and second
  if (second.location < first.location + first.length) {
    result.location = second.location;
    NSUInteger end = MIN(first.location + first.length, second.location + second.length);
    result.length = end - result.location;
  }
  
  return result;    
}

- (void)drawSelectionWithRange:(NSRange)selectionRange {
  // If selection range empty, do not draw
  if (self.selectedRange.length == 0 || self.selectedRange.location == NSNotFound)
    return;
  
  // set the fill color to the selection color
  [[UIColor colorWithRed:0.92 green:0.94 blue:0.97 alpha:1.0] setFill];

  // Iterate over the lines in our CTFrame, looking for lines that intersect
  // with the given selection range, and draw a selection rect for each intersection
  CGMutablePathRef path = CGPathCreateMutable();
  CGPathAddRect(path, NULL, self.bounds);
  CTFrameRef frame = CTFramesetterCreateFrame(self.framesetter, CFRangeMake(0, self.attributedText.length), path, NULL);
  NSArray* lines = (NSArray*)CTFrameGetLines(frame);
  CGPoint origins[lines.count];
  // Get coordinate and bounds information for the intersection text range
  CTFrameGetLineOrigins(frame, CFRangeMake(0, 0), origins);
  for (int i = 0; i < lines.count; ++i) {
    CTLineRef line = (CTLineRef)[lines objectAtIndex:i];
    CFRange lineRange = CTLineGetStringRange(line);
    NSRange range = NSMakeRange(lineRange.location, lineRange.length);
    NSRange intersection = [self rangeIntersection:range withSecond:selectionRange];
    if (intersection.location != NSNotFound && intersection.length > 0) {
      // The text range for this line intersects our selection range
      CGFloat xStart = CTLineGetOffsetForStringIndex(line, intersection.location, NULL);
      CGFloat xEnd = CTLineGetOffsetForStringIndex(line, intersection.location + intersection.length, NULL);
      CGFloat ascent, descent;
      CTLineGetTypographicBounds(line, &ascent, &descent, NULL);
      // Create a rect for the intersection and draw it with selection color
      CGPoint origin = origins[i];
      CGRect selectionRect = CGRectMake(xStart, origin.y - descent, xEnd - xStart, ascent + descent);
      selectionRect = CGRectInset(selectionRect, -2, -2);
      [[UIBezierPath bezierPathWithRoundedRect:selectionRect cornerRadius:2] fill];
    }
  }
  CFRelease(frame);
  CFRelease(path);
}

- (void)clearSelection {
  self.selectedRange = NSMakeRange(0, 0);
  [self setNeedsDisplay];
}

#pragma mark - UILabel

- (void)setHighlighted:(BOOL)highlighted {
  [super setHighlighted:highlighted];
  [self setNeedsDisplay];
}

- (void)drawTextInRect:(CGRect)rect {
  if (!self.attributedText) {
    [super drawTextInRect:rect];
    return;
  }
  
  CGContextRef c = UIGraphicsGetCurrentContext();
  CGContextSetTextMatrix(c, CGAffineTransformIdentity);

  // Inverts the CTM to match iOS coordinates (otherwise text draws upside-down; Mac OS's system is different)
  CGContextTranslateCTM(c, 0.0f, self.bounds.size.height);
  CGContextScaleCTM(c, 1.0f, -1.0f);
  
  CGRect textRect = rect;
  CFRange textRange = CFRangeMake(0, self.attributedText.length);
  CFRange fitRange;

  // First, adjust the text to be in the center vertically, if the text size is smaller than the drawing rect
  CGSize textSize = CTFramesetterSuggestFrameSizeWithConstraints(self.framesetter, textRange, NULL, textRect.size, &fitRange);
  
  if (textSize.height < textRect.size.height) {
    CGFloat yOffset = 0.0f;
    switch (self.verticalAlignment) {
      case TTTAttributedLabelVerticalAlignmentTop:
        break;
      case TTTAttributedLabelVerticalAlignmentCenter:
        yOffset = floorf((textRect.size.height - textSize.height) / 2.0f);
        break;
      case TTTAttributedLabelVerticalAlignmentBottom:
        yOffset = (textRect.size.height - textSize.height);
        break;
    }

    textRect.origin = CGPointMake(textRect.origin.x, textRect.origin.y + yOffset);
    textRect.size = CGSizeMake(textRect.size.width, textRect.size.height - yOffset);
  }
  
  // Second, trace the shadow before the actual text, if we have one
  if (self.shadowColor && !self.highlighted) {
    CGRect shadowRect = textRect;
    // We subtract the height, not add it, because the whole scene is inverted.
    shadowRect.origin = CGPointMake(shadowRect.origin.x + self.shadowOffset.width, shadowRect.origin.y - self.shadowOffset.height);
    
    // Override the text's color attribute to whatever the shadow color is
    if (!self.shadowFramesetter) {
      NSMutableAttributedString* shadowAttrString = [[self.attributedText mutableCopy] autorelease];
      [shadowAttrString addAttribute:(NSString*)kCTForegroundColorAttributeName value:(id)[self.shadowColor CGColor] range:NSMakeRange(0, self.attributedText.length)];
      self.shadowFramesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)shadowAttrString);
    }
    
    [self drawFramesetter:self.shadowFramesetter textRange:textRange inRect:shadowRect context:c];
  }
  
  // Finally, draw the text or highlighted text itself (on top of the shadow, if there is one)
  if (self.highlightedTextColor && self.highlighted) {
    if (!self.highlightFramesetter) {
      NSMutableAttributedString* mutableAttributedString = [[self.attributedText mutableCopy] autorelease];
      [mutableAttributedString addAttribute:(NSString*)kCTForegroundColorAttributeName value:(id)[self.highlightedTextColor CGColor] range:NSMakeRange(0, mutableAttributedString.length)];
      self.highlightFramesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)mutableAttributedString);
    }
    [self drawFramesetter:self.highlightFramesetter textRange:textRange inRect:textRect context:c];
  } else if (self.selectedRange.length > 0) {
    [self drawSelectionWithRange:self.selectedRange];
    CGColorRef textColor = [UIColor colorWithRed:0.48 green:0.61 blue:0.8 alpha:1.0].CGColor;
    NSMutableAttributedString* mutableAttributedString = [[self.attributedText mutableCopy] autorelease];
    [mutableAttributedString addAttribute:(NSString*)kCTForegroundColorAttributeName value:(id)textColor range:self.selectedRange];
    CTFramesetterRef selectionFrame = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)mutableAttributedString);
    [self drawFramesetter:selectionFrame textRange:textRange inRect:textRect context:c];
    CFRelease(selectionFrame);
  } else {
    [self drawFramesetter:self.framesetter textRange:textRange inRect:textRect context:c];
  }  
}

#pragma mark - UIControl

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];	
	NSTextCheckingResult* result = [self linkAtPoint:[touch locationInView:self]];
  if (result && self.delegate) {
    self.selectedRange = result.range;
    [self setNeedsDisplay];
    return;
  }

  [super touchesBegan:touches withEvent:event];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  if (self.selectedRange.length > 0) {
    self.selectedRange = NSMakeRange(0, 0);
    [self setNeedsDisplay];
    return;
  }

  [super touchesCancelled:touches withEvent:event];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];	
	NSTextCheckingResult* result = [self linkAtPoint:[touch locationInView:self]];
  
  if (result && self.delegate) {
    switch (result.resultType) {
      case NSTextCheckingTypeLink:
        if ([self.delegate respondsToSelector:@selector(attributedLabel:didSelectLinkWithURL:)]) {
          [self.delegate attributedLabel:self didSelectLinkWithURL:result.URL];
        }
        break;
      case NSTextCheckingTypeAddress:
        if ([self.delegate respondsToSelector:@selector(attributedLabel:didSelectLinkWithAddress:)]) {
          [self.delegate attributedLabel:self didSelectLinkWithAddress:result.addressComponents];
        }
        break;
      case NSTextCheckingTypePhoneNumber:
        if ([self.delegate respondsToSelector:@selector(attributedLabel:didSelectLinkWithPhoneNumber:)]) {
          [self.delegate attributedLabel:self didSelectLinkWithPhoneNumber:result.phoneNumber];
        }
        break;
      case NSTextCheckingTypeDate:
        if (result.timeZone && [self.delegate respondsToSelector:@selector(attributedLabel:didSelectLinkWithDate:timeZone:duration:)]) {
          [self.delegate attributedLabel:self didSelectLinkWithDate:result.date timeZone:result.timeZone duration:result.duration];
        } else if ([self.delegate respondsToSelector:@selector(attributedLabel:didSelectLinkWithDate:)]) {
          [self.delegate attributedLabel:self didSelectLinkWithDate:result.date];
        }
        break;
    }
    [self performSelector:@selector(clearSelection) withObject:nil afterDelay:0.2];
    return;
  }

  [super touchesEnded:touches withEvent:event];
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];	
	NSTextCheckingResult* result = [self linkAtPoint:[touch locationInView:self]];
  if (result && self.delegate) {
    self.selectedRange = NSMakeRange(0, 0);
    [self setNeedsDisplay];
    return;
  }
  [super touchesMoved:touches withEvent:event];
}

#pragma mark - UIView

- (CGSize)sizeThatFits:(CGSize)size {
  if (!self.attributedText)
    return [super sizeThatFits:size];

  CGSize suggestedSize = CTFramesetterSuggestFrameSizeWithConstraints(self.framesetter, CFRangeMake(0, [self.attributedText length]), NULL, CGSizeMake(size.width, CGFLOAT_MAX), NULL);
  return CGSizeMake(ceilf(suggestedSize.width), ceilf(suggestedSize.height));
}

@end
