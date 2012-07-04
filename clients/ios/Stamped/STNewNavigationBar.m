//
//  STNewNavigationBar.m
//  Stamped
//
//  Created by Landon Judkins on 7/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STNewNavigationBar.h"

#import <QuartzCore/QuartzCore.h>
#import <CoreText/CoreText.h>
#import "UIColor+Stamped.h"
#import "Util.h"

@interface STNewNavigationBar ()
- (void)initialize;
- (CGPathRef)newPathForTitle;

@property (nonatomic, readonly, retain) UIView* contentView;
@property (nonatomic, readwrite, retain) UIView* currentHeader;
@property (nonatomic, readwrite, retain) UIView* nextHeader;
@property (nonatomic, readwrite, assign) BOOL animating;
@property (nonatomic, readonly) CALayer* ripplesLayer;

- (void)setHeader:(UIView*)view animated:(BOOL)animated;

@end

@implementation STNewNavigationBar

@synthesize ripplesLayer = ripplesLayer_;
@synthesize hideLogo = hideLogo_;
@synthesize string = string_;
@synthesize contentView = _contentView;
@synthesize currentHeader = _currentHeader;

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
    [_currentHeader release];
    [_contentView release];
    [super dealloc];
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextSetFillColorWithColor(ctx, [UIColor blackColor].CGColor);
    CGContextFillRect(ctx, rect);
    CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect byRoundingCorners:(UIRectCornerTopLeft | UIRectCornerTopRight) cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath);
    CGContextClip(ctx);
    
    [[UIImage imageNamed:@"nav_bar_no_logo"] drawInRect:rect];
    /*
     if (hideLogo_ && self.topItem.title) {
     
     [[UIImage imageNamed:@"nav_bar_no_logo"] drawInRect:rect];
     for (UIView *view in self.subviews) {
     if ([view isKindOfClass:NSClassFromString(@"UINavigationItemView")]) {
     view.hidden = YES;
     }
     }
     
     UIFont *font = [UIFont boldSystemFontOfSize:18];
     [[UIColor colorWithRed:0.0f green:0.333f blue:0.8f alpha:1.0f] setFill];
     CGSize size = [self.topItem.title sizeWithFont:font];
     [self.topItem.title drawInRect:CGRectMake(floorf((self.bounds.size.width-size.width)/2), floorf((self.bounds.size.height-size.height)/2), size.width, size.height) withFont:font lineBreakMode:UILineBreakModeWordWrap];
     
     }
     */
}

- (UIView*)stampedHeader {
    return [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamped_logo"]] autorelease];
}

- (void)setHeader:(UIView *)view animated:(BOOL)animated {
    CGRect bounds = CGRectMake(0, 0, self.contentView.frame.size.width, self.contentView.frame.size.height);
    view.frame = [Util centeredAndBounded:view.frame.size inFrame:bounds];
    if (animated) {
        [UIView animateWithDuration:.4 animations:^{
            
        } completion:^(BOOL finished) {
            
        }];
    }
    else {
        [self.currentHeader removeFromSuperview];
        self.currentHeader = view;
        [self.contentView addSubview:view];
    }
}

- (void)initialize {
    
    self.layer.masksToBounds = NO;
    
    CGRect bounds = CGRectMake(0, 0, self.frame.size.width, self.frame.size.height);
    UIView* contentView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 180, self.frame.size.height)] autorelease];
    [self addSubview:contentView];
    contentView.frame = [Util centeredAndBounded:contentView.frame.size inFrame:bounds];
    contentView.clipsToBounds = YES;
    _contentView = [contentView retain];
    [self setHeader:[self stampedHeader] animated:NO];
    
    CGFloat ripplesY = CGRectGetMaxY(self.bounds);
    ripplesLayer_ = [[CALayer alloc] init];
    ripplesLayer_.contentsScale = [[UIScreen mainScreen] scale];
    ripplesLayer_.frame = CGRectMake(0, ripplesY, 320, 3);
    ripplesLayer_.contentsGravity = kCAGravityResizeAspect;
    ripplesLayer_.contents = (id)[UIImage imageNamed:@"nav_bar_ripple"].CGImage;
    [self.layer addSublayer:ripplesLayer_];
    [ripplesLayer_ release];
    
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

- (void)showUserStrip:(BOOL)show forUser:(id<STUser>)user {
    
    if (show) {
        
        float r,g,b;
        [Util splitHexString:user.primaryColor toRed:&r green:&g blue:&b];
        
        float r2,g2,b2;
        [Util splitHexString:user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
        
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height, self.bounds.size.width, 4.0f)];
        view.backgroundColor = [UIColor whiteColor];
        [self insertSubview:view atIndex:0];
        [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
            size_t _numLocations = 2;
            CGFloat _locations[2] = { 0.0, 1.0 };
            CGFloat _colors[8] = { r, g, b, 1.0f, r2, g2, b2, 1.0f };
            CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
            CGColorSpaceRelease(_rgb);
            
            CGPoint start = CGPointMake(rect.origin.x, CGRectGetMidY(rect));
            CGPoint end = CGPointMake(rect.size.width, CGRectGetMidY(rect));
            
            CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsBeforeStartLocation | kCGGradientDrawsAfterEndLocation);
            CGGradientRelease(gradient);
            
            [[UIColor whiteColor] setStroke];
            CGContextMoveToPoint(ctx, 0.0f, rect.size.height - 0.5f);
            CGContextAddLineToPoint(ctx, rect.size.width, rect.size.height - 0.5f);
            CGContextStrokePath(ctx);
            
        }];
        [view release];
        view.layer.shadowPath = [UIBezierPath bezierPathWithRect:view.bounds].CGPath;
        view.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        view.layer.shadowRadius = 4.0f;
        view.layer.shadowOpacity = 0.15f;
        _userStrip = view;
        
    } else {
        
        if (_userStrip) {
            [_userStrip removeFromSuperview], _userStrip=nil;
        }
        
    }
    
    
}

@end
