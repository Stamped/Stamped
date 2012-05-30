//
//  STStampTitleView.m
//  Stamped
//
//  Created by Devin Doty on 5/29/12.
//
//

#import "STStampTitleView.h"

@interface STStampTitleView (Internal)
- (void)clearLayout;
@end

@implementation STStampTitleView
@synthesize title=_title;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

    }
    return self;
}


- (void)dealloc {
    [self clearLayout];
    [_title release], _title=nil;
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    if (_frame==NULL || self.title==nil) return;
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CTFrameDraw(_frame, ctx);    
    
}

- (void)clearLayout {
    
    if (_framesetter!=NULL) {
        CFRelease(_framesetter);
        _framesetter = NULL;
    }
    
    if (_frame!=NULL) {
        CFRelease(_frame);
        _frame = NULL;
    }
    
}



#pragma mark - Getters

- (CGSize)sizeConstrainedToSize:(CGSize)size {
    
    if (_framesetter==NULL) {
        return CGSizeZero;
    }
    
    return size = CTFramesetterSuggestFrameSizeWithConstraints(_framesetter, CFRangeMake(0, 0), NULL, size, NULL);

}


#pragma mark - Setters

- (void)setTitle:(NSString *)title {
    [_title release], _title=nil;
    _title = [title copy];
    
    [self clearLayout];
    
    CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica", 35, NULL);

    NSAttributedString *string = [[NSAttributedString alloc] initWithString:_title];
    _framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string);
    CGPathRef _path = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
	_frame = CTFramesetterCreateFrame(_framesetter, CFRangeMake(0, 0), _path, NULL);
    [self setNeedsDisplay];
    [string release];
    
}

- (void)setString:(NSAttributedString *)string{

    /*
    
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)self.string);
    CGPathRef _path = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
	_frame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, 0), _path, NULL);											
    [self setNeedsDisplay];
    
    CGFloat lineSpacing = 2;            
    CTParagraphStyleSetting settings[1] = { { kCTParagraphStyleSpecifierLineSpacing, sizeof(CGFloat), &lineSpacing } };
    
    CTParagraphStyleRef paragraphRef = CTParagraphStyleCreate(settings, 1);
    [mutableAttributedString addAttribute:(id)kCTParagraphStyleAttributeName value:(id)paragraphRef range:NSMakeRange(0, mutableAttributedString.string.length)];
    CFRelease(paragraphRef);
    
    CTFramesetterRef _framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)mutableAttributedString);
    
    self.textSize320 = CGSizeMake(ceilf(size.width), ceilf(size.height));
    CGPathRef _path = [UIBezierPath bezierPathWithRect:CGRectMake(0, 0, self.textSize320.width, self.textSize320.height)].CGPath;
    _frame = CTFramesetterCreateFrame(_framesetter, CFRangeMake(0, 0), _path, NULL);											
    self.attributedString = mutableAttributedString;
    [mutableAttributedString release];
    CFRelease(_framesetter);

    
    */
    
}


@end
