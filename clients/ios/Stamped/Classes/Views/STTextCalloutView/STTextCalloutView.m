//
//  STTextCalloutView.m
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import "STTextCalloutView.h"
#import <CoreText/CoreText.h>

@implementation STTextCalloutView

- (id)init {
    if ((self = [super init])) {
        CATextLayer *layer = [CATextLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.backgroundColor = [UIColor clearColor].CGColor;
        layer.alignmentMode = @"center";
        [self.layer addSublayer:layer];
        _textLayer = layer;
    }
    return self;
}

- (CGFloat)boundingWidthForAttributedString:(NSAttributedString *)attributedString {
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString( (CFMutableAttributedStringRef) attributedString); 
    CGSize suggestedSize = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(0, 0), NULL, CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX), NULL);
    CFRelease(framesetter);
    return suggestedSize.width;
}

- (void)setTitle:(NSString*)title boldText:(NSString*)boldText {
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"Helvetica Neue" : (CFStringRef)@"Helvetica", 11, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)[UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    if (boldText) {
        [string setAttributes:boldStyle range:[string.string rangeOfString:boldText]];
    }
    
    CGFloat width = ceilf([self boundingWidthForAttributedString:string]);

    CGRect frame = self.frame;
    frame.size.width = MAX((width + 20.0f), 60.0f);
    self.frame = frame;
    
    _textLayer.frame = CGRectMake((self.bounds.size.width-width)/2, 14.0f, width, 14);
    _textLayer.string = string;
    [string release];
    
}


@end
