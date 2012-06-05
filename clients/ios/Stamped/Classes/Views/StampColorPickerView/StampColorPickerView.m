//
//  StampColorPickerView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "StampColorPickerView.h"

#define kStampSize 57.0f
#define kStampGap 2.5

@interface StampPickerButton : UIControl {
    UIView *_background;
}
@property(nonatomic,readonly,strong) UIImageView *imageView;
@property(nonatomic,readonly,strong) UILabel *titleLabel;
@end

@interface StampPickerView : UIControl {
    UIImageView *_checkView;
    CALayer *_colorLayer;
}
@property(nonatomic,readonly,retain) UIColor *color1;
@property(nonatomic,readonly,retain) UIColor *color2;
- (void)removeSelection;
- (void)setTopColor:(UIColor*)color bottomColor:(UIColor*)color;
@end

@interface StampColorPickerView ()
- (NSArray*)defaultColorsAtIndex:(NSInteger)index;
@end

@implementation StampColorPickerView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        _views = [[NSMutableArray alloc] initWithCapacity:10];
        
        for (NSInteger i = 0; i < 10; i++) {
            
            StampPickerView *view = [[StampPickerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, kStampSize, kStampSize)];
            [view addTarget:self action:@selector(stampPicked:) forControlEvents:UIControlEventTouchUpInside];
            view.backgroundColor = [UIColor clearColor];
            NSArray *color = [self defaultColorsAtIndex:i];
            [view setTopColor:[color objectAtIndex:0] bottomColor:[color objectAtIndex:1]];
            [self addSubview:view];
            [_views addObject:view];
            [view release];
            
            if (i == 0) {
                [view setSelected:YES];
            }
            
        }
        
        StampPickerButton *button = [[StampPickerButton alloc] initWithFrame:CGRectMake(10.0f, self.bounds.size.height - 48.0f, (self.bounds.size.width-30.0f)/2, 45.0f)];
        button.imageView.image = [UIImage imageNamed:@"stamp_customize_icon.png"];
        button.titleLabel.text = @"Customize";
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleRightMargin;
        [button addTarget:self action:@selector(customize:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        [button release];
        
        button = [[StampPickerButton alloc] initWithFrame:CGRectMake(20.0f + (self.bounds.size.width-30.0f)/2, self.bounds.size.height - 48.0f, (self.bounds.size.width-30.0f)/2, 45.0f)];
        button.titleLabel.text = @"Randomize";
        button.imageView.image = [UIImage imageNamed:@"stamp_randomize_icon.png"];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
        [button addTarget:self action:@selector(randomize:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        [button release];
        
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGFloat originX = 10.0f;
    CGFloat originY = 2.0f;
    CGRect frame;
    for (StampPickerView *view in _views) {
    
        frame = view.frame;
        frame.origin.x = originX;
        frame.origin.y = originY;
        view.frame = frame;
        
        originX = floorf(originX + kStampSize + kStampGap);
        if (originX > (self.bounds.size.width - kStampSize)) {
            originX = 10.0f;
            originY += (kStampSize + kStampGap);
        }
        
    }
}

- (NSArray*)defaultColorsAtIndex:(NSInteger)index {

    UIColor *color1 = nil;
    UIColor *color2 = nil;
    
    switch (index) {
        case 0:
            color1 =  [UIColor colorWithRed:0.0f green:0.290f blue:0.698f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.0f green:0.3411f blue:0.819f alpha:1.000];
            break;
        case 1:
            color1 =  [UIColor colorWithRed:0.517f green:0.0f blue:0.294f alpha:1.0f];
            color2 =  [UIColor colorWithRed:1.0f green:0.0f blue:0.917f alpha:1.000];
            break;
        case 2:
            color1 =  [UIColor colorWithRed:0.0f green:0.501f blue:0.0f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.211f green:0.764f blue:0.223f alpha:1.000];
            break;
        case 3:
            color1 =  [UIColor colorWithRed:1.0f green:0.494f blue:0.0f alpha:1.0f];
            color2 =  [UIColor colorWithRed:1.0f green:0.917f blue:0.0f alpha:1.000];
            break;
        case 4:
            color1 =  [UIColor colorWithRed:0.317f green:0.768f blue:0.733f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.568f green:0.929f blue:0.909f alpha:1.000];
            break;
        case 5:
            color1 =  [UIColor colorWithRed:1.0f green:0.082f blue:0.0f alpha:1.0f];
            color2 =  [UIColor colorWithRed:1.0f green:0.415f blue:0.0f alpha:1.000];
            break;
        case 6:
            color1 =  [UIColor colorWithRed:0.2588f green:1.0f blue:0.0f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.988f green:0.145f blue:0.6f alpha:1.0f];
            break;
        case 7:
            color1 =  [UIColor colorWithRed:0.341f green:0.0f blue:0.807f alpha:1.0f];
            color2 =  [UIColor colorWithRed:1.0f green:0.376f blue:0.0f alpha:1.000];
            break;
        case 8:
            color1 =  [UIColor colorWithRed:0.827f green:0.113f blue:0.19f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.313f green:0.721f blue:0.74f alpha:1.000];
            break;
        case 9:
            color1 =  [UIColor colorWithRed:0.113f green:0.298f blue:0.827f alpha:1.0f];
            color2 =  [UIColor colorWithRed:0.333f green:0.745f blue:0.3137f alpha:1.000];
            break;
            
        default:
            break;
    }
    
    
    return [NSArray arrayWithObjects:color1, color2, nil];
    
}


#pragma mark - Getters

- (NSArray*)colors {
    
    StampPickerView *view = nil;
    
    for (StampPickerView *aView in _views) {
        if (aView.selected) {
            view = aView;
            break;
        }
    }
    
    if (view != nil) {
        return [NSArray arrayWithObjects:view.color1, view.color2, nil];
    }
    
    return nil;
    
}


#pragma mark - Actions

- (void)stampPicked:(StampPickerView*)sender {
 
    [_views makeObjectsPerformSelector:@selector(removeSelection)];
    [sender setSelected:YES];
    
    if ([(id)delegate respondsToSelector:@selector(stampColorPickerView:selectedColors:)]) {
        [self.delegate stampColorPickerView:self selectedColors:[NSArray arrayWithObjects:sender.color1, sender.color2, nil]];
    }
    
}

- (void)randomize:(id)sender {
    
    [_views makeObjectsPerformSelector:@selector(randomize)];
    
}

- (void)customize:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stampColorPickerViewSelectedCustomize:)]) {
        [self.delegate stampColorPickerViewSelectedCustomize:self];
    }
    
}


@end


#pragma mark - StampPickerView

@implementation StampPickerView
@synthesize color1=_color1;
@synthesize color2=_color2;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        _color1 = [[UIColor blackColor] retain];
        _color2 = [[UIColor blackColor] retain];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_picker_white_border.png"]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        [self addSubview:imageView];
        [imageView release];
        
        CGRect frame = imageView.frame;
        frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        imageView.frame = frame;
        
        CALayer *layer = [CALayer layer];
        layer.frame = CGRectMake(0.0f, 0.0f, 46.0f, 46.0f);
        layer.position = CGPointMake(imageView.bounds.size.width/2, (imageView.bounds.size.height/2)-2.0f);
        layer.contentsScale = [[UIScreen mainScreen] scale];
        [imageView.layer addSublayer:layer];
        _colorLayer = layer;

    }
    return self;
    
}

- (void)dealloc {
    [_color2 release], _color2=nil;
    [_color1 release], _color1=nil;
    [super dealloc];
}

- (void)setTopColor:(UIColor*)color bottomColor:(UIColor*)color2 animated:(BOOL)animated {
    
    [_color2 release], _color2=nil;
    [_color1 release], _color1=nil;
    
    _color1 = [color retain];
    _color2 = [color2 retain];
    
    UIGraphicsBeginImageContextWithOptions(_colorLayer.bounds.size, NO, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);
    
    CGContextClipToMask(ctx, rect, [UIImage imageNamed:@"stamp_46pt_texture.png"].CGImage);
    drawStampGradient(_color1.CGColor, _color2.CGColor, ctx);
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    BOOL disabled = [CATransaction disableActions];
    [CATransaction setDisableActions:!animated];
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.25f];
    _colorLayer.contents = (id)image.CGImage;
    [CATransaction commit];
    [CATransaction setDisableActions:disabled];

}

- (void)setTopColor:(UIColor*)color bottomColor:(UIColor*)color2 {
    [self setTopColor:color bottomColor:color2 animated:NO];
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    
    if (selected) {
        
        if (!_checkView) {
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_picker_check.png"]];
            [self addSubview:imageView];
            [imageView release];
            _checkView = imageView;
            imageView.layer.position = CGPointMake(self.bounds.size.width/2, (self.bounds.size.height/2)+1.0f);            
        }
        
        
    } else {
        
        if (_checkView) {
            [_checkView removeFromSuperview];
            _checkView = nil;
        }
        
    }
    
    
}

- (void)removeSelection {
    
    [self setSelected:NO];
    
}

- (UIColor*)randomColor {
    
    float r, g, b;

    r = arc4random() % 255;
    g = arc4random() % 255;
    b = arc4random() % 255;

    return [UIColor colorWithRed:r/255.0f green:g/255.0f blue:b/255.0f alpha:1.0f];
    
}

- (void)randomize {
    if (self.selected) return;
    
    [self setTopColor:[self randomColor] bottomColor:[self randomColor] animated:YES];
    
}


@end


#pragma mark - StampPickerButton

@implementation StampPickerButton
@synthesize imageView=_imageView;
@synthesize titleLabel=_titleLabel;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
        background.userInteractionEnabled = NO;
        background.backgroundColor = [UIColor clearColor];
        background.contentMode = UIViewContentModeRedraw;
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:background];
        [background setDrawingHanlder:^(CGContextRef cx, CGRect rect) {
            
            BOOL highlighted = (self.highlighted || self.selected);
            rect = CGRectInset(rect, 2.0f, 2.0f);
            CGContextRef ctx = UIGraphicsGetCurrentContext();
            CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:2].CGPath;
            CGContextAddPath(ctx, path);
            
            CGContextSaveGState(ctx);
            CGContextClip(ctx);
            
            if (highlighted) {
                drawGradient([UIColor colorWithRed:0.004f green:0.514f blue:0.976f alpha:1.0f].CGColor, [UIColor colorWithRed:0.129f green:0.286f blue:0.918f alpha:1.0f].CGColor, ctx);
            } else {
                drawGradient([UIColor colorWithRed:0.9921f green:0.9921f blue:0.9921f alpha:1.0f].CGColor, [UIColor colorWithRed:0.9529f green:0.9529f blue:0.9529f alpha:1.0f].CGColor, ctx);
            }
            
            CGContextRestoreGState(ctx);
            
             CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 2.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.05f].CGColor);
             [[UIColor colorWithRed:0.862f green:0.862f blue:0.862f alpha:1.0f] setStroke];
             CGContextAddPath(ctx, path);
             CGContextStrokePath(ctx);
            
            CGContextAddPath(ctx, path);
            
            if (highlighted) {
                
                [[UIColor whiteColor] setStroke];
                CGContextStrokePath(ctx);
                
            } else {
                
                CGContextReplacePathWithStrokedPath(ctx);
                CGContextClip(ctx);
                drawGradient([UIColor colorWithRed:0.886f green:0.886f blue:0.886f alpha:1.0f].CGColor, [UIColor colorWithRed:0.862f green:0.862f blue:0.862f alpha:1.0f].CGColor, ctx);
                
            }
            
        }];
        [background release];
        _background = background;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont boldSystemFontOfSize:11];
        label.highlightedTextColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectZero];
        [self addSubview:imageView];
        _imageView = [imageView retain];
        [imageView release];
        
        
    }
    return self;
}

- (void)dealloc {
    [_imageView release];
    [_titleLabel release];
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    CGRect frame = self.titleLabel.frame;
    frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
    frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
    self.titleLabel.frame = frame;
    
    [self.imageView sizeToFit];
    frame = self.imageView.frame;
    frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
    frame.origin.x = (CGRectGetMinX(self.titleLabel.frame) - self.imageView.bounds.size.width);
    self.imageView.frame = frame;
    
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [_background setNeedsDisplay];
    [self.titleLabel setHighlighted:highlighted];
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    [_background setNeedsDisplay];
    [self.titleLabel setHighlighted:selected];
}


@end

