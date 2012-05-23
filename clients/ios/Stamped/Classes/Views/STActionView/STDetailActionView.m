//
//  STActionView.m
//  Stamped
//
//  Created by Devin Doty on 5/16/12.
//
//

#import "STDetailActionView.h"
#import "STTextPopoverView.h"

#define kActionItemWidth 40
#define kActionItemGap 10

@interface STDetailAction : NSObject <STDetailActionItem>
- (id)initWithImageTitle:(NSString*)title imageTitleHi:(NSString*)titleHi imageTitleSel:(NSString*)titleSel target:(id)target action:(SEL)action;
@end
@implementation STDetailAction
@synthesize imageName;
@synthesize imageNameHighlighted;
@synthesize imageNameSelected;
@synthesize target=_target;
@synthesize selector;
- (id)initWithImageTitle:(NSString*)title imageTitleHi:(NSString*)titleHi imageTitleSel:(NSString*)titleSel target:(id)target action:(SEL)action {
    if ((self = [super init])) {
        self.imageName = title;
        self.imageNameHighlighted = titleHi;
        self.imageNameSelected = titleSel;
        self.target = target;
        self.selector = action;
    }
    return self;
}

- (void)dealloc
{
    self.imageName = nil;
    self.imageNameHighlighted = nil;
    self.imageNameSelected = nil;
    [super dealloc];
}

@end

@implementation STDetailActionView

@synthesize items=_items;
@synthesize itemKeys=_itemKeys;
@synthesize expanded=_expanded;
@synthesize delegate=_delegate;
@synthesize minItemsToShow=_minItemsToShow;

- (void)commonInit {
    
    self.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
    
    _minItemsToShow = 4;
    _itemViews = [[NSArray array] retain];
    _items = [[NSArray array] retain];
    
    UIImage *image = [UIImage imageNamed:@"st_detail_action_bg"];
    UIImageView *background = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
    [self addSubview:background];
    CGRect frame = background.frame;
    frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
    frame.size.width = self.bounds.size.width;
    background.frame = frame;
    
}

- (id)initWithStamp:(id<STStamp>)stamp delegate:(id)delegate {
    if ((self = [super initWithFrame:CGRectZero])) {
        
        [self commonInit];
        
        NSMutableDictionary *items = [NSMutableDictionary dictionary];
        NSMutableArray *itemKeys = [NSMutableArray array];
        
        STDetailAction *button = [[[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_like.png" 
                                                               imageTitleHi:@"sDetailBar_btn_like_active.png" 
                                                              imageTitleSel:@"sDetailBar_btn_like_selected.png" 
                                                                     target:self 
                                                                     action:@selector(likeButtonHit:)] autorelease];
        [items setObject:button forKey:@"todo"];
        [itemKeys addObject:@"todo"];
        
        
        button = [[[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_todo.png" 
                                               imageTitleHi:@"sDetailBar_btn_todo_selected.png" 
                                              imageTitleSel:@"sDetailBar_btn_todo_selected.png" 
                                                     target:self action:@selector(todobuttonHit:)] autorelease];
        [items addObject:button];
        [itemKeys addObject:@"todo"];
        
        button = [[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_comment.png" imageTitleHi:@"sDetailBar_btn_comment_active.png" target:self action:@selector(buttonHit:)];
        [items addObject:button];
        
        button = [[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_restamp.png" imageTitleHi:@"sDetailBar_btn_restamp_active.png" target:self action:@selector(buttonHit:)];
        [items addObject:button];
        [button release];
        
        button = [[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_share.png" imageTitleHi:@"sDetailBar_btn_share_active.png" target:self action:@selector(buttonHit:)];
        [items addObject:button];
        [button release];
        
        button = [[STDetailAction alloc] initWithImageTitle:@"sDetailBar_btn_more.png" imageTitleHi:@"sDetailBar_btn_more_active.png" target:self action:@selector(expand:)];
        [items addObject:button];
        [button release];

        self.items = (id)items;        
    }
    return self;
}

- (id)initWithItems:(NSArray<STDetailActionItem>*)items {
    if ((self = [super initWithFrame:CGRectZero])) {
        [self commonInit];
        self.items = items;
    }
    return self;
}

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        [self commonInit];
    }
    return self;
}

- (void)dealloc {
    _delegate = nil;
    [_items release], _items = nil;
    [_itemViews release], _itemViews = nil;
    [super dealloc];
}


#pragma mark - Layout

- (CGFloat)width {
    
    NSInteger count = [_itemViews count];
    
    if (_expanded) {
        return floorf((count * kActionItemWidth) + (count * kActionItemGap));
    }
    
    count = MIN(self.minItemsToShow, count);
    return MAX(floorf(kActionItemWidth + (kActionItemGap*2)), floorf((count * kActionItemWidth) + (count * kActionItemGap)));
    
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGRect frame = self.frame;
    frame.size.width = [self width];
    frame.size.height = 44.0f;
    frame.origin.x = (self.superview.bounds.size.width - (frame.size.width+10.0f));
    frame.origin.y = (self.superview.bounds.size.height - (frame.size.height+10.0f));
    self.frame = frame;

}


#pragma mark - Setters

- (void)setItems:(NSArray<STDetailActionItem>*)items {
    [_items release], _items = nil;
    _items = [items retain];
        
    CGFloat originX = kActionItemGap;
    NSMutableArray *array = [[NSMutableArray alloc] initWithCapacity:[_items count]];
    NSInteger index = 0;
    for (NSObject <STDetailActionItem> *item in _items) {
    
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];        
        button.autoresizingMask = UIViewAutoresizingFlexibleHeight;
        [button setImage:[UIImage imageNamed:item.imageName] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:item.imageNameHighlighted] forState:UIControlStateHighlighted];
        [button setImage:[UIImage imageNamed:item.imageNameHighlighted] forState:UIControlStateSelected];
        [button addTarget:item.target action:item.selector forControlEvents:UIControlEventTouchUpInside];
        button.frame = CGRectMake(originX, -2.0f, kActionItemWidth, self.bounds.size.height);
        [self addSubview:button];
        
        if (!_expanded && (index < (self.minItemsToShow-1) || index == ([_items count]-1))) {
            originX += (kActionItemGap + kActionItemWidth);
        } else {
            button.hidden = YES;
        }
        
        [array addObject:button];
        index++;
        
    }
    
    _itemViews = [array retain];
    [self setNeedsLayout];
    
}

- (void)setExpanded:(BOOL)expanded animated:(BOOL)animated {
    _expanded = expanded;
    
    [UIView animateWithDuration:0.25f animations:^{
        
        CGRect frame = self.frame;
        frame.size.width = [self width];
        frame.origin.x = (self.superview.bounds.size.width - (frame.size.width+10.0f));
        self.frame = frame;
        
        NSInteger index = 0;
        CGFloat originX = kActionItemGap;
        for (UIButton *button in _itemViews) {
            
            if (!_expanded) {
                
                if ((index < (self.minItemsToShow-1) || index == ([_itemViews count]-1))) {
                    button.frame = CGRectMake(originX, 0.0f, kActionItemWidth, self.bounds.size.height);
                    originX += (kActionItemGap + kActionItemWidth);
                } else {
                    button.hidden = YES;
                }
                
            } else {
                
                button.frame = CGRectMake(originX, 0.0f, kActionItemWidth, self.bounds.size.height);
                originX += (kActionItemGap + kActionItemWidth);
              
                
            }
            
            index++;
            
        }
        
        
    }];
    
    
    if (_expanded) {
        
        float delay = 0.1f;
        
        for (UIButton *button in _itemViews) {
            
            if (button.hidden) {
                
                CAAnimationGroup *animation = [CAAnimationGroup animation];
                animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
                animation.duration = 0.25f;
                animation.beginTime = [button.layer convertTime:CACurrentMediaTime() toLayer:nil] + delay;
                
                CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
                scale.calculationMode = kCAAnimationCubic;
                scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.2f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:1.0f], nil];
                
                CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
                opacity.fromValue = [NSNumber numberWithFloat:0.0f];
                opacity.toValue = [NSNumber numberWithFloat:1.0f];
                
                [animation setAnimations:[NSArray arrayWithObjects:opacity, nil]];
                [button.layer addAnimation:animation forKey:nil];
                //button.hidden = NO;

                dispatch_after(dispatch_time(DISPATCH_TIME_NOW, delay * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void){
                    button.hidden = NO;
                });
                
                delay += 0.04f;

            }
            
        }        
        
    }
   
    
        
}

- (void)setExpanded:(BOOL)expanded {
    [self setExpanded:expanded animated:YES];
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
            
    STTextPopoverView *view = [[STTextPopoverView alloc] initWithFrame:CGRectZero];
    view.title = NSLocalizedString(@"Liked!", nil);
    CGPoint pos = [[sender layer] position];
    pos.y -= 30.0f;
    [view showFromView:self.superview position:[self convertPoint:pos toView:self.superview] animated:YES];
    [view hideDelayed:1.0f];
    [view release];
    
    return;
    NSInteger index = [_itemViews indexOfObject:sender];
    if (index != NSNotFound) {
        
        if ([(id)_delegate respondsToSelector:@selector(stActionView:itemSelectedAtIndex:)]) {
            [self.delegate stActionView:self itemSelectedAtIndex:index];
        }
        
    }
    
}

- (void)expand:(id)sender {
    
    [self setExpanded:!_expanded animated:YES];
    [sender setSelected:_expanded];

}


@end
