//
//  PostStampGraphView.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampGraphView.h"
#import "STStampContainerView.h"
#import <CoreText/CoreText.h>
#import "ImageLoader.h"

@interface STPostGraphCell : UIControl {
    UIImage *_icon;
    UIView *_columnView;
    UIView *_iconView;
}
@property(nonatomic,readonly) CGFloat barHeight;
@property(nonatomic,readonly) NSInteger stampCount;
@property(nonatomic,readonly,copy) NSString *name;
@property(nonatomic,readonly,copy) NSString *category;
- (void)setupWithDistributionItem:(id<STDistributionItem>)item barHeight:(CGFloat)barHeight;
@end

@implementation PostStampGraphView
@synthesize user=_user;
@synthesize loading=_loading;
@synthesize category;

- (id)initWithFrame:(CGRect)frame {

    if ((self = [super initWithFrame:frame])) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(20.0f, 11.0f, 16.0f, 16.0f)];
        [self addSubview:imageView];
        imageView.contentMode = UIViewContentModeScaleAspectFit;
        _imageView = imageView;
        [imageView release];
        
        CATextLayer *textLayer = [CATextLayer layer];
        textLayer.contentsScale = [[UIScreen mainScreen] scale];
        [self.layer addSublayer:textLayer];
        _titleLayer = textLayer;
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake((self.bounds.size.width-290.0f)/2, 38.0f, 290.0f, 86.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        _graphContainer = view;
        [view release];
        
        CGFloat originX = 0.0f;
        for (NSInteger i = 0; i < 6; i++) {
            STPostGraphCell *cell = [[STPostGraphCell alloc] initWithFrame:CGRectMake(originX, 0.0f, 45.0f, _graphContainer.bounds.size.height)];
            [_graphContainer addSubview:cell];
            originX += 49.0f;
            [cell release];
        }
        
    }
    return self;
}

- (void)dealloc {
    
    self.category = nil;
    [_user release], _user=nil;
    [super dealloc];
}

- (void)reloadData {
    if (!self.user) return;
        
    id<STDistributionItem> relevantItem = nil;
    NSInteger maxStamps = 1;
    for (id<STDistributionItem> item in self.user.distribution) {
        if ([item.category isEqualToString:self.category]) {
            relevantItem = item;
        }
        maxStamps = MAX(item.count.integerValue, maxStamps);
    }

    if (relevantItem) {
        [[ImageLoader sharedLoader] imageForURL:[NSURL URLWithString:relevantItem.icon] completion:^(UIImage *image, NSURL *url) {
            _imageView.image = image;
        }];
    }
    
    NSString *ordinalText = [NSString stringWithFormat:@"%i", [relevantItem.count integerValue]];
    NSString *title = [NSString stringWithFormat:@"That's your %@ stamp in %@", ordinalText, [relevantItem.category capitalizedString]];
 
    UIColor *textColor = [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f];
    UIColor *boldTextColor = [UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f];
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 11, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)boldTextColor.CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)textColor.CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    [string setAttributes:boldStyle range:[string.string rangeOfString:ordinalText]];
    
    [defaultStyle release];
    [boldStyle release];
    
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString( (CFMutableAttributedStringRef) string); 
    CGSize size = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(0, 0), NULL, CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX), NULL);
    CFRelease(framesetter);
    
    _titleLayer.string = string;
    [string release];
    _titleLayer.frame = CGRectMake(42.0f, 12.0f, size.width, size.height);
    
    NSInteger index = 0;
    for (id<STDistributionItem> item in self.user.distribution) {
        STPostGraphCell *cell = [[_graphContainer subviews] objectAtIndex:index];
        if (item == relevantItem) {
            cell.highlighted = YES;
        }
        [cell setupWithDistributionItem:item barHeight:MAX((item.count.integerValue * (cell.bounds.size.height-18.0f)) / maxStamps, 3)];
        index++;
    }
    
    
}


#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    _loading=loading;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
            view.layer.zPosition = 10;
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
            [self addSubview:view];
            _activityView = view;
            [view release];
            
            [_activityView startAnimating];

            CGRect frame = _activityView.frame;
            frame.size = CGSizeMake(18.0f, 18.0f);
            frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
            frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
            _activityView.frame = frame;
            
        }

    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview];
            _activityView=nil;
        }
        
    }

}

- (void)setUser:(id<STUserDetail>)user {
    [_user release], _user=nil;
    _user = [user retain];

    [self setLoading:NO];
    [self reloadData];
    
}

@end


#pragma mark - STPostGraphCell

@implementation STPostGraphCell
@synthesize barHeight=_barHeight;
@synthesize name=_name;
@synthesize category=_category;
@synthesize stampCount=_stampCount;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-16.0f, self.bounds.size.width, 16.0f)];
        view.backgroundColor = [UIColor clearColor];
        [self addSubview:view];
        [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {

            if (_icon) {
                
                CGContextSaveGState(ctx);
                CGRect imageRect = CGRectMake((rect.size.width-_icon.size.width)/2, 0.0f, _icon.size.width, _icon.size.height);
                CGContextTranslateCTM(ctx, 0, rect.size.height);
                CGContextScaleCTM(ctx, 1.0, -1.0);
                
                if (self.highlighted) {
                    [[UIColor colorWithRed:0.325f green:0.662f blue:0.160f alpha:1.0f] setFill];
                } else {
                    [[UIColor colorWithWhite:0.749 alpha:1.0f] setFill];
                }
                
                CGContextClipToMask(ctx, imageRect, _icon.CGImage);
                CGContextFillRect(ctx, imageRect);
                CGContextRestoreGState(ctx);
            }
            
        }];
        _iconView = view;
        [view release];
        
        view = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-18.0f, self.bounds.size.width, 1.0f)];
        view.contentMode = UIViewContentModeRedraw;
        view.backgroundColor = self.backgroundColor;
        [self addSubview:view];
        [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
           
            CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:2.0f].CGPath);
            CGContextClip(ctx);
            [[UIImage imageNamed:self.highlighted ? @"post_graph_bg_hi.png" : @"post_graph_bg.png"] drawAsPatternInRect:rect];
            
        }];
        _columnView = view;
        [view release];

    }
    return self;
}

- (void)dealloc {
    [_icon release], _icon=nil;
    [_category release], _category=nil;
    [_name release], _name=nil;
    [super dealloc];
}

- (void)setCategory:(NSString *)category {
    [_category release], _category=nil;
    _category = [category retain];
    
    [_icon release], _icon=nil;
    _icon = [[self iconForName:_category.lowercaseString] retain];
    [self setNeedsDisplay];

}

- (UIImage*)iconForName:(NSString*)name {
    
    return [UIImage imageNamed:[NSString stringWithFormat:@"graph_%@_icon.png", name]];
    
}

- (void)setupWithDistributionItem:(id<STDistributionItem>)item barHeight:(CGFloat)barHeight {
    
    _barHeight = barHeight;
    [_icon release], _icon=nil;
    _icon = [[self iconForName:item.name.lowercaseString] retain];    
    [_name release], _name=nil;
    _name = [item.name.lowercaseString copy];
    _category = [item.category copy];
    _stampCount = item.count.integerValue;
    
    _barHeight = MAX(_barHeight, 1.0f);

    [_iconView setNeedsDisplay];
    [_columnView setNeedsDisplay];
    
    _iconView.alpha = 0.0f;
    
    [UIView animateWithDuration:0.3f delay:0.3f options:UIViewAnimationOptionCurveEaseInOut animations:^{
        
        _iconView.alpha = 1.0f;
        _columnView.frame = CGRectMake(0.0f, self.bounds.size.height - (_barHeight+18.0f), self.bounds.size.width, _barHeight);
        
    } completion:^(BOOL finished){
    
        if (self.highlighted) {
            _columnView.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:_columnView.bounds cornerRadius:2.0f].CGPath;
            _columnView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
            _columnView.layer.shadowRadius = 2.0f;
        }
        _columnView.layer.shadowOpacity = self.highlighted ? 0.2f : 0.0f;
        [_columnView setNeedsDisplay];

    }];
    
}


@end