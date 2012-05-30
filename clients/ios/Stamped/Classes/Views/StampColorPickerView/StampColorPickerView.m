//
//  StampColorPickerView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "StampColorPickerView.h"

#define kStampSize 57.0f
#define kStampGap 6.0f

@interface StampPickerButton : UIButton
@end

@interface StampPickerView : UIControl {
    UIImageView *_checkView;
    UIColor *_color1;
    UIColor *_color2;
}
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
            view.backgroundColor = [UIColor clearColor];
            NSArray *color = [self defaultColorsAtIndex:i];
            [view setTopColor:[color objectAtIndex:0] bottomColor:[color objectAtIndex:1]];
            [self addSubview:view];
            [_views addObject:view];
            [view release];
            
        }
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button addTarget:self action:@selector(radomize:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button addTarget:self action:@selector(customize:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGFloat originX = kStampGap;
    CGFloat originY = 0.0f;
    CGRect frame;
    for (StampPickerView *view in _views) {
    
        frame = view.frame;
        frame.origin.x = originX;
        frame.origin.y = originY;
        view.frame = frame;
        
        originX = floorf(originX + kStampSize + kStampGap);
        if (originX > (self.bounds.size.width - kStampSize)) {
            originX = kStampGap;
            originY = (kStampSize + kStampGap);
        }
        
    }
}

- (NSArray*)defaultColorsAtIndex:(NSInteger)index {

    UIColor *color1 = nil;
    UIColor *color2 = nil;
    
    color1 =  [UIColor colorWithRed:0.113f green:0.298f blue:0.827f alpha:1.0f];
    color2 =  [UIColor colorWithRed:0.333f green:0.745f blue:0.3137f alpha:1.000];
    
    return [NSArray arrayWithObjects:color1, color2, nil];
    
}



#pragma mark - Actions

- (void)randomize:(id)sender {
    
    
    
}

- (void)customize:(id)sender {
    
    
    
}



@end


#pragma mark - StampPickerView

@implementation StampPickerView

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        _color1 = [[UIColor blackColor] retain];
        _color2 = [[UIColor blackColor] retain];
        
    }
    return self;
    
}

- (void)dealloc {
    [_color2 release], _color2=nil;
    [_color1 release], _color1=nil;
    [super dealloc];
}

- (void)setTopColor:(UIColor*)color bottomColor:(UIColor*)color2 {
    
    [_color2 release], _color2=nil;
    [_color1 release], _color1=nil;

    _color1 = [color retain];
    _color2 = [color2 retain];
    
    [self setNeedsDisplay];
    
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    
    UIImage *image = [UIImage imageNamed:@"stamp_picker_white_border.png"];
    [image drawInRect:CGRectMake((rect.size.width-image.size.width)/2, (rect.size.height-image.size.height)/2, image.size.width, image.size.height)];
    
    
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);

    image = [UIImage imageNamed:@"stamp_46pt_texture.png"];
    CGRect imageRect = CGRectMake((rect.size.width-image.size.width)/2, floorf(rect.size.height-(image.size.height-1.0f)), image.size.width, image.size.height);
    CGContextClipToMask(ctx, imageRect, image.CGImage);
    drawStampGradient(_color1.CGColor, _color2.CGColor, ctx);
    
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    
    if (selected) {
        
        if (!_checkView) {
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_picker_check.png"]];
            [self addSubview:imageView];
            [imageView release];
            _checkView = imageView;
        }
        
        
    } else {
        
        if (_checkView) {
            [_checkView removeFromSuperview];
            _checkView = nil;
        }
        
    }
    
    
}


@end