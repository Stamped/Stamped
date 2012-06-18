//
//  STGraphCallout.m
//  Stamped
//
//  Created by Devin Doty on 6/17/12.
//
//

#import "STGraphCallout.h"
#import <CoreText/CoreText.h>

@implementation STGraphCallout
@synthesize category;
@synthesize delegate;

- (id)init {
    
    if ((self = [super init])) {
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button addTarget:self action:@selector(disclosureHit:) forControlEvents:UIControlEventTouchUpInside];
        button.imageView.contentMode = UIViewContentModeCenter;
        [button setImage:[UIImage imageNamed:@"st_callout_disclosure_arrow.png"] forState:UIControlStateNormal];
        button.frame = CGRectMake(self.bounds.size.width - 46.0f, 0.0f, 44.0f, 44.0f);
        [self addSubview:button];
        _disclosureButton = button;
        
        
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
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 11, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)[UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    if (boldText) {
        [string setAttributes:boldStyle range:[string.string rangeOfString:boldText]];
    }
    [defaultStyle release];
    [boldStyle release];
    
    CGFloat width = ceilf([self boundingWidthForAttributedString:string]);
    
    CATextLayer *layer = [CATextLayer layer];
    layer.contentsScale = [[UIScreen mainScreen] scale];
    layer.frame = CGRectMake(16.0f, 14.0f, width, 14);
    layer.backgroundColor = [UIColor clearColor].CGColor;
    layer.alignmentMode = @"center";
    layer.string = string;
    [self.layer addSublayer:layer];
    [string release];
    
    CGRect frame = self.frame;
    frame.size.width = (width + 60.0f);
    self.frame = frame;
    
}

- (void)disclosureHit:(id)sender {
    
    [self.delegate disclosureHit:self];
    
}

@end