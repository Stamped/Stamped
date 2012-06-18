//
//  STUserGraphView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserGraphView.h"
#import "STSimpleUserDetail.h"
#import "ImageLoader.h"
#import "STCalloutView.h"
#import "STGraphCallout.h"
#import <CoreText/CoreText.h>
#import <CoreGraphics/CoreGraphics.h>


@interface STUserGraphCell : UIControl {
    UIImage *_icon;
}
@property(nonatomic,readonly) CGFloat barHeight;
@property(nonatomic,readonly) NSInteger stampCount;
@property(nonatomic,readonly,copy) NSString *name;
@property(nonatomic,readonly,copy) NSString *category;
- (void)setupWithDistributionItem:(id<STDistributionItem>)item;
@end


#pragma mark - STUserGraphView

@interface STUserGraphView (Internal)
- (void)cellTapped:(STUserGraphCell*)cell;
@end

@implementation STUserGraphView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor whiteColor];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithWhite:0.749 alpha:1.0f];
        label.font = [UIFont systemFontOfSize:12];
        [self addSubview:label];
        [label release];
        _countLabel = label;
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake((self.bounds.size.width-290.0f)/2, 60.0f, 290.0f, 144.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        [view release];
        _graphContainer = view;
        
        CGFloat originX = 0.0f;
        for (NSInteger i = 0; i < 6; i++) {
            STUserGraphCell *cell = [[STUserGraphCell alloc] initWithFrame:CGRectMake(originX, 0.0f, 45.0f, _graphContainer.bounds.size.height)];
            [cell addTarget:self action:@selector(cellTapped:) forControlEvents:UIControlEventTouchUpInside];
            [_graphContainer addSubview:cell];
            originX += 49.0f;
            [cell release];
        }
        
        
    }
    return self;
}

- (void)setupWithUser:(STSimpleUserDetail *)user {
    if (![user respondsToSelector:@selector(distribution)]) return;
    
    NSInteger maxStamps = 1;
    NSInteger totalStamps = 0;
    for (id<STDistributionItem> item in user.distribution) {
        maxStamps = MAX(item.count.integerValue, maxStamps);
        totalStamps += item.count.integerValue;
    }
    
    _countLabel.text = [NSString stringWithFormat:@"%i stamp%@ total.", totalStamps, (totalStamps==1) ? @"" : @"s"];
    [_countLabel sizeToFit];
    
    CGRect frame = _countLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = CGRectGetMaxY(_graphContainer.frame) + 20.0f;
    _countLabel.frame = frame;

    NSInteger index = 0;
    STUserGraphCell *maxCell = nil;
    for (id<STDistributionItem> item in user.distribution) {
        STUserGraphCell *cell = [[_graphContainer subviews] objectAtIndex:index];
        [cell setupWithDistributionItem:item];
        index++;
        
        if (item.count.integerValue == maxStamps) {
            maxCell = cell;
        }
        
    }
    if (maxCell) {
        [self cellTapped:maxCell];
    }
    
}

- (void)cellTapped:(STUserGraphCell*)cell {
    
    UIView *view = [[UIView alloc] initWithFrame:self.bounds];
    [self addSubview:view];
    [view release];
    
    UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
    gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
    [view addGestureRecognizer:gesture];
    [gesture release];
    
    STGraphCallout *callout = [[STGraphCallout alloc] init];
    callout.delegate = self;
    [view addSubview:callout];
    [callout setTitle:[NSString stringWithFormat:@"%i stamp%@ in %@", cell.stampCount, (cell.stampCount==1) ? @"" : @"s", cell.category] boldText:cell.category];
    CGPoint point = CGPointMake(cell.bounds.size.width/2, (cell.bounds.size.height - cell.barHeight)+4.0f);
    [callout showFromPosition:[view convertPoint:point fromView:cell] animated:YES];
    callout.category = cell.category;
    [callout release];
    
    _calloutView = view;
    
}

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    UIView *subview = [[gestureRecognizer.view subviews] lastObject];
    CGRect frame = subview.frame;
    frame.size.height -= 10.0f; // remove drop shadow
    return !CGRectContainsPoint(frame, [gestureRecognizer locationInView:gestureRecognizer.view]);
    
}

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    if (_calloutView) {
        [_calloutView removeFromSuperview], _calloutView=nil;
    }

    CGPoint point = [gesture locationInView:_graphContainer];
    for (STUserGraphCell *view in _graphContainer.subviews) {
        if (CGRectContainsPoint(view.frame, point)) {
            [self cellTapped:view];
            break;
        }
    }
        
}


#pragma makr - STGraphCalloutDelegate

- (void)disclosureHit:(STGraphCallout*)callout {
    
    if ([(id)delegate respondsToSelector:@selector(stUserGraphView:selectedCategory:)]) {
        [self.delegate stUserGraphView:self selectedCategory:callout.category];
    }
    [callout.superview removeFromSuperview];
    
}

@end


#pragma mark - STUserGraphCell

@implementation STUserGraphCell
@synthesize barHeight=_barHeight;
@synthesize name=_name;
@synthesize category=_category;
@synthesize stampCount=_stampCount;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor whiteColor];
    }
    return self;
}

- (void)dealloc {
    [_icon release], _icon=nil;
    [_category release], _category=nil;
    [_name release], _name=nil;
    [super dealloc];
}

- (UIImage*)iconForName:(NSString*)name {
    
    return [UIImage imageNamed:[NSString stringWithFormat:@"graph_%@_icon.png", name]];
    
}

- (void)setupWithDistributionItem:(id<STDistributionItem>)item {
        
    CGFloat x = item.count.integerValue;
    CGFloat coeff = MIN((.5 - (1 / powf((x + 6), .4))) * 80/33,1);
    _barHeight = MAX((coeff * self.bounds.size.height), 2);
    
    [_icon release], _icon=nil;
    _icon = [[self iconForName:item.name.lowercaseString] retain];
    [self setNeedsDisplay];
    
    [_name release], _name=nil;
    _name = [item.name.lowercaseString copy];
    _category = [item.category copy];
    _stampCount = item.count.integerValue;
    
    CGRect barRect = CGRectMake(0.0f, self.bounds.size.height - _barHeight, self.bounds.size.width, _barHeight);
    self.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:barRect cornerRadius:2.0f].CGPath;
    self.layer.shadowOpacity = 0.2f;
    self.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    self.layer.shadowRadius = 4.0f;
    
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    [[UIColor colorWithRed:0.937f green:0.960f blue:0.988f alpha:1.0f] setStroke];
    CGFloat originY = 0.5f;
    CGContextMoveToPoint(ctx, 0.0f, originY);
    for (NSInteger i = 0; i<4; i++) {
        CGContextAddLineToPoint(ctx, rect.size.width, originY);
        originY+=36.0f;
        CGContextMoveToPoint(ctx, 0.0f, originY);
    }
    CGContextStrokePath(ctx);
    
    CGContextSaveGState(ctx);
    CGRect barRect = CGRectMake(0.0f, rect.size.height - _barHeight, rect.size.width, _barHeight);
    CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:barRect cornerRadius:2.0f].CGPath);
    CGContextClip(ctx);
    [[UIImage imageNamed:@"user_graph_bg.png"] drawAsPatternInRect:rect];
    CGContextRestoreGState(ctx);
    
    if (_icon) {

        BOOL highlight = (_barHeight/2) > _icon.size.height+4.0f;
        
        CGFloat originY = (_icon.size.height+4.0f);
        if (!highlight && _barHeight > 4.0f) {
            originY = _barHeight + 4.0f;
        }

        CGRect imageRect = CGRectMake((rect.size.width-_icon.size.width)/2, originY, _icon.size.width, _icon.size.height);
        CGContextTranslateCTM(ctx, 0, rect.size.height);
        CGContextScaleCTM(ctx, 1.0, -1.0);
        if (highlight) {
            [[UIColor whiteColor] setFill];
            CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, -1.0f), 0.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.1f].CGColor);
        } else {
            [[UIColor colorWithWhite:0.749 alpha:1.0f] setFill];
        }
        CGContextClipToMask(ctx, imageRect, _icon.CGImage);
        CGContextFillRect(ctx, imageRect);

    }

    
    
}

@end

