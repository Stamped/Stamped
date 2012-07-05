//
//  STSegmentedControl.m
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import "STSegmentedControl.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"

#define kSegmentCellHeight 58
#define kSegmentBuffer 15

@interface STSegmentedControlCell : UIControl {
    UIView *_backgroundView;
}
@property(nonatomic,copy) NSString *title;
@property(nonatomic,retain) UIImage *image;
@property(nonatomic,assign) UIRectCorner corners;
@end

@interface STSegmentedControl ()
@property(nonatomic,retain) NSArray *segmentViews;
@property(nonatomic,retain) UIView *contentView;
@end

@implementation STSegmentedControl
@synthesize items=_items;
@synthesize selectedSegmentIndex=_selectedSegmentIndex;
@synthesize segmentViews;
@synthesize contentView;


- (id)initWithItems:(NSArray*)items {
    
    self.backgroundColor = [UIColor clearColor];

    CGRect frame = CGRectZero;
    frame.size.height = kSegmentCellHeight+(kSegmentBuffer*2);
    frame.size.width = [[UIScreen mainScreen] applicationFrame].size.width;

    if ((self = [super initWithFrame:frame])) {
        
        self.items = items;
        self.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        
    }
    return self;
    
}

- (void)dealloc {
    self.segmentViews = nil;
    self.contentView = nil;
    [_items release], _items=nil;
    [super dealloc];
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGRect frame;
    CGFloat originX = kSegmentBuffer;
    CGFloat width = floorf((self.bounds.size.width - kSegmentBuffer*2) / [self.segmentViews count]);
    for (STSegmentedControlCell *cell in self.segmentViews) {
    
        frame = cell.frame;
        frame.origin = CGPointMake(originX, (self.bounds.size.height-kSegmentCellHeight)/2);
        frame.size.width = width;
        cell.frame = frame;
        originX+=width;
    
    }
    
}


#pragma mark - Actions

- (void)segmentSelected:(id)segment {
    
    NSInteger index = [self.segmentViews indexOfObject:segment];
    
    if (index != NSNotFound) {
        self.selectedSegmentIndex = index;
    }
    
}


#pragma mark - Setters

- (void)setItems:(NSArray *)items {
    [_items release], _items=nil;
    _items = [items retain];
    
    [self.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    NSMutableArray *array = [[NSMutableArray alloc] initWithCapacity:[_items count]];
    
    NSInteger index = 0;
    for (NSString *item in _items) {

        STSegmentedControlCell *cell = [[STSegmentedControlCell alloc] initWithFrame:CGRectMake(0.0f, (self.bounds.size.height-kSegmentCellHeight)/2, 0.0f, kSegmentCellHeight)];
        cell.title = item;
        NSString *imageString = [item lowercaseString];
        imageString = [imageString stringByReplacingOccurrencesOfString:@" " withString:@"_"];
        if ([imageString isEqualToString:@"café"]) {
            imageString = @"cafe";
        }
        cell.image = [UIImage imageNamed:[NSString stringWithFormat:@"entity_create_%@.png", imageString]];
        [cell addTarget:self action:@selector(segmentSelected:) forControlEvents:UIControlEventTouchUpInside];
        cell.selected = index == _selectedSegmentIndex;
        
        if (index == 0 && index == [items count]-1) {
            cell.corners = UIRectCornerAllCorners;
        } else if (index == 0) {
            cell.corners = UIRectCornerTopLeft | UIRectCornerBottomLeft;
        } else if (index == [items count]-1) {
            cell.corners = UIRectCornerTopRight | UIRectCornerBottomRight;
        } else {
            cell.corners = 0;
        }
        
        [self addSubview:cell];
        [array addObject:cell];
        [cell release];
        index ++;
    }
    
    self.segmentViews = array;
    [array release];
    
    [self setNeedsLayout];
    
}

- (void)setSelectedSegmentIndex:(NSInteger)selectedSegmentIndex {
    _selectedSegmentIndex=selectedSegmentIndex;
    
    NSInteger index = 0;
    for (STSegmentedControlCell *cell in self.segmentViews) {
        cell.selected = index == _selectedSegmentIndex;
        index++;
    }
    
    NSArray *targets = [[self allTargets] allObjects];
    
    for (id target in targets) {
        
        NSArray *actions = [self actionsForTarget:target forControlEvent:UIControlEventValueChanged];
        for (id action in actions) {
            SEL selector = NSSelectorFromString(action);
            if ([target respondsToSelector:selector]) {
                [target performSelector:selector withObject:self];
            }
        }
    }
        
}


@end



#pragma mark - STSegmentedControlCell 

@implementation STSegmentedControlCell
@synthesize title;
@synthesize image;
@synthesize corners;

- (id)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
        background.userInteractionEnabled = NO;
        background.backgroundColor = [UIColor clearColor];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:background];
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            if (!self.selected) {
                rect.origin.y += 0.5f;
                rect.size.height -= 2.0f;
            } else {
                rect.size.height -= 1.0f;
            }
            
            if (self.corners == (UIRectCornerBottomRight | UIRectCornerTopRight)) {
                rect.size.width-=0.5f;
            } else if (self.corners == (UIRectCornerTopLeft | UIRectCornerBottomLeft)) {
                rect.origin.x += 0.5f;
                rect.size.width -= 0.5f;
            } else if (self.corners == UIRectCornerAllCorners) {
                rect.origin.x += 0.5f;
                rect.size.width -= 1.0f;
            }
            
            CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:rect byRoundingCorners:self.corners cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath;
            CGContextAddPath(ctx, path);
            
            if (self.selected) {
                
                CGContextClip(ctx);
                drawGradient([UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f].CGColor, [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f].CGColor, ctx);
                CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 2.0f), 5.6, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.2f].CGColor);
                
                path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, -.5, -.5) byRoundingCorners:self.corners cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath;
                CGContextAddPath(ctx, path);
                CGContextStrokePath(ctx);
                
            } else {
                
                UIColor *bottomColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:0.6f];
                UIColor *topColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.8f];
                
                // drop shadow
                CGContextSaveGState(ctx);
                CGContextSetFillColorWithColor(ctx, [UIColor whiteColor].CGColor);
                CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 1.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.05].CGColor);
                CGContextAddPath(ctx, path);
                CGContextFillPath(ctx);
                CGContextAddPath(ctx, path);
                CGContextClip(ctx);
                CGContextClearRect(ctx, rect);
                CGContextRestoreGState(ctx);
                
                // gradient fill
                CGContextSaveGState(ctx);
                CGContextAddPath(ctx, path);
                CGContextClip(ctx);
                drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
                
                // inner shadow
                CGFloat corner = 2.0f;
                CGFloat originY = corner;
                CGFloat originX = rect.origin.x;
                CGContextSetStrokeColorWithColor(ctx, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.4f].CGColor);
                CGContextMoveToPoint(ctx, originX, originY + corner);
                CGContextAddQuadCurveToPoint(ctx, originX, originY, originX + corner, originY);
                CGContextAddLineToPoint(ctx, rect.size.width-(originX+corner), originY);
                CGContextAddQuadCurveToPoint(ctx, rect.size.width-originX, originY, rect.size.width-originX, originY + corner);
                CGContextStrokePath(ctx);
                CGContextRestoreGState(ctx);
                
                // gradient stroke
                CGContextSaveGState(ctx);
                bottomColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:0.6f];
                topColor = [UIColor colorWithRed:0.8f green:0.8f blue:0.8f alpha:0.8f];
                CGContextAddPath(ctx, path);
                CGContextReplacePathWithStrokedPath(ctx);
                CGContextClip(ctx);
                drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
                CGContextRestoreGState(ctx);

            }
            
            if (self.title) {
                
                if (!self.selected) {
                    [[UIColor colorWithWhite:0.6f alpha:1.0f] setFill];
                } else {
                    [[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f] setFill];
                }
                
                UIFont *font = [UIFont systemFontOfSize:10];
                CGSize size = [self.title sizeWithFont:font];
                [self.title drawInRect:CGRectMake(floorf((rect.size.width-size.width)/2), rect.size.height - 24.0f, size.width, size.height) withFont:font];
                
            }
            
            if (self.image) {
                
                CGRect imageRect = CGRectMake(floorf((rect.size.width-image.size.width)/2), 12.0f, image.size.width, image.size.height);
                [self.image drawInRect:imageRect];
                
                if (self.selected) {
                    
                    imageRect.origin.y = rect.size.height - (imageRect.origin.y + imageRect.size.height);
                    CGContextSetFillColorWithColor(ctx, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor);
                    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
                    CGContextScaleCTM(ctx, 1.0f, -1.0f);
                    CGContextClipToMask(ctx, imageRect, self.image.CGImage);
                    CGContextFillRect(ctx, rect);

                }
                
            }
            
            
        }];
        _backgroundView = background;
        [background release];
        
    }
    return self;
    
}

- (void)dealloc {
    self.image = nil;
    self.title = nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [_backgroundView setNeedsDisplay];
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    [_backgroundView setNeedsDisplay];
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [_backgroundView setNeedsDisplay];
}



@end

