//
//  STConsumptionToolbar.m
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionToolbar.h"
#import "STConfiguration.h"
#import "Util.h"
#import "STButton.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import <QuartzCore/QuartzCore.h>

//Position
static NSString* _buttonHeightKey = @"Consumption.toolbar.button.height";
static NSString* _buttonPaddingKey = @"Consumption.toolbar.button.padding";
static NSString* _buttonInnerPaddingKey = @"Consumption.toolbar.button.inner_padding";
static NSString* _buttonCornerRadiusKey = @"Consumption.toolbar.button.corner_radius";

@interface STConsumptionToolbar ()

- (CGFloat)generateViewsWithItem:(STConsumptionToolbarItem*)item andOuput:(NSMutableArray*)outputArray;

@property (nonatomic, readonly, retain) STConsumptionToolbarItem* root;
@property (nonatomic, readwrite, retain) NSArray* currentViews;
@property (nonatomic, readwrite, retain) UIView* toolbarContents;
@property (nonatomic, readwrite, retain) STConsumptionToolbarItem* currentItem;
@property (nonatomic, readonly, retain) UIView* backButton;

@end

@implementation STConsumptionToolbar

@synthesize root = root_;
@synthesize delegate = delegate_;
@synthesize currentViews = currentViews_;
@synthesize toolbarContents = toolbarContents_;
@synthesize currentItem = currentItem_;
@synthesize slider = slider_;
@synthesize backButton = _backButton;

- (id)initWithRootItem:(STConsumptionToolbarItem*)item andScope:(STStampedAPIScope)scope
{
    self = [super init];
    if (self) {
        root_ = [item retain];
        toolbarContents_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, self.frame.size.width * 2, self.frame.size.height)];
        [self addSubview:toolbarContents_];
        if (LOGGED_IN) {
        CGPoint buttonOrigin = CGPointMake(280, 10);
        UIImage* normalImage = [UIImage imageNamed:@"scope_drag_inner_friends"];
        UIImage* activeImage = [Util whiteMaskedImageUsingImage:normalImage];
        STButton* button = [STButton buttonWithNormalImage:normalImage activeImage:activeImage target:self andAction:@selector(viewScopeButtonClicked:)];
        [Util reframeView:button withDeltas:CGRectMake(buttonOrigin.x, buttonOrigin.y, 0, 0)];
        [toolbarContents_ addSubview:button];
        }
        UIImage* categoryImage = [UIImage imageNamed:@"scope_drag_inner_fof"];
        UIImage* activeCategory = [Util whiteMaskedImageUsingImage:categoryImage];
        STButton* backButton = [STButton buttonWithNormalImage:categoryImage activeImage:activeCategory target:self andAction:@selector(categoriesButtonClicked:)];
        _backButton = [backButton retain];
        backButton.hidden = YES;
        [Util reframeView:backButton withDeltas:CGRectMake(self.frame.size.width + 10, 10, 0, 0)];
        [toolbarContents_ addSubview:backButton];
        
        slider_ = [[STSliderScopeView alloc] initWithFrame:CGRectMake(self.frame.size.width + 60, 0.0f, self.bounds.size.width - 120, self.bounds.size.height)];
        slider_.layer.shadowOpacity = 0.0f;
        slider_.scope = LOGGED_IN ? STStampedAPIScopeFriends : STStampedAPIScopeEveryone;
        slider_.hidden = YES;
        [toolbarContents_ addSubview:slider_];
        [self updateWithItem:item animated:NO];
    }
    return self;
}

- (void)dealloc
{
    [root_ release];
    [currentViews_ release];
    [toolbarContents_ release];
    [currentItem_ release];
    [_backButton release];
    [super dealloc];
}

- (void)viewScopeButtonClicked:(id)nothing {
    self.slider.hidden = NO;
    self.backButton.hidden = NO;
    [UIView animateWithDuration:.25 animations:^{
        self.toolbarContents.frame = CGRectMake(-320, self.toolbarContents.frame.origin.y, self.toolbarContents.frame.size.width, self.toolbarContents.frame.size.height);
    }];
}

- (void)categoriesButtonClicked:(id)nothing {
    self.slider.hidden = YES;
    self.backButton.hidden = YES;
    [UIView animateWithDuration:.25 animations:^{
        self.toolbarContents.frame = CGRectMake(0, self.toolbarContents.frame.origin.y, self.toolbarContents.frame.size.width, self.toolbarContents.frame.size.height);
    }];
}

- (STButton*)consumptionButtonWithName:(NSString*)name icon:(UIImage*)icon selector:(SEL)selector {
    CGFloat height = [[STConfiguration value:_buttonHeightKey] floatValue];
    CGFloat padding = [[STConfiguration value:_buttonInnerPaddingKey] floatValue];
    UIImageView* imageView = nil;
    if (icon) {
        imageView = [[[UIImageView alloc] initWithImage:icon] autorelease];
        imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:CGRectMake(padding, 0, imageView.frame.size.width, height)];
    }
    UIView* text = [Util viewWithText:name
                                 font:[UIFont stampedBoldFont]
                                color:[UIColor stampedBlackColor]
                                 mode:UILineBreakModeTailTruncation
                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    text.frame = [Util centeredAndBounded:text.frame.size 
                                  inFrame:CGRectMake(
                                                     imageView ? CGRectGetMaxX(imageView.frame)+padding : padding,
                                                     0,
                                                     text.frame.size.width,
                                                     height)];
    CGFloat buttonWidth = CGRectGetMaxX(text.frame) + 5;
    CGRect buttonFrame = CGRectMake(0, 0, buttonWidth, height);
    UIView* views[2];
    CGFloat cornerRadius = [[STConfiguration value:_buttonCornerRadiusKey] floatValue];
    for (NSInteger i = 0; i < 2; i++) {
        UIView* aView = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
        CGFloat shadowInset = 1;
        [Util reframeView:aView withDeltas:CGRectMake(0, shadowInset, 0, -shadowInset)];
        aView.layer.cornerRadius = cornerRadius - 1;
        NSArray* colors;
        if (i == 0) {
            colors = [NSArray arrayWithObjects:
                      [UIColor colorWithWhite:120/255.0 alpha:1],
                      [UIColor colorWithWhite:83/255.0 alpha:1],
                      nil];
        }
        else {
            colors = [NSArray arrayWithObjects:
                      [UIColor colorWithWhite:200/255.0 alpha:1],
                      [UIColor colorWithWhite:140/255.0 alpha:1],
                      nil];
        }
        [Util addGradientToLayer:aView.layer withColors:colors vertical:YES];
        views[i] = aView;
    }
    STButton* button = [[[STButton alloc] initWithFrame:buttonFrame 
                                             normalView:views[0]
                                             activeView:views[1]
                                                 target:self 
                                              andAction:selector] autorelease];
    button.backgroundColor = [UIColor colorWithWhite:148/255.0 alpha:1];
    button.layer.cornerRadius = cornerRadius;
    button.layer.shadowColor = [UIColor blackColor].CGColor;
    button.layer.shadowOffset = CGSizeMake(0, 2);
    button.layer.shadowRadius = 4;
    button.layer.shadowOpacity = .7;
    if (imageView) {
        [button addSubview:imageView];
    }
    [button addSubview:text];
    return button;
}

- (void)backButtonClicked:(id)notImportant {
    [self updateWithItem:self.currentItem.parent animated:YES];
}

- (void)childChosen:(STConsumptionToolbarItem*)item {
    [self updateWithItem:item animated:YES];
}

- (CGFloat)generateViewsWithItem:(STConsumptionToolbarItem*)item andOuput:(NSMutableArray*)outputArray {
    CGFloat width = 0;
    CGFloat padding = [[STConfiguration value:_buttonPaddingKey] floatValue];
    CGFloat innerPadding = [[STConfiguration value:_buttonInnerPaddingKey] floatValue];
    CGFloat height = [[STConfiguration value:_buttonHeightKey] floatValue];
    CGFloat cornerRadius = [[STConfiguration value:_buttonCornerRadiusKey] floatValue];
    
    if (item.parent) {
        UIImage* backIcon = [Util gradientImage:item.icon withPrimaryColor:@"797979" secondary:@"535353" andStyle:STGradientStyleVertical];
        UIImageView* backIconView = [[[UIImageView alloc] initWithImage:backIcon] autorelease];
        CGRect buttonFrame = CGRectMake(0, 0, MAX(backIconView.frame.size.width + 2 * innerPadding, height), height);
        backIconView.frame = [Util centeredAndBounded:backIconView.frame.size inFrame:buttonFrame];
        UIView* views[2];
        for (NSInteger i = 0; i < 2; i++) {
            UIView* aView = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
            NSArray* colors;
            if (i == 0) {
                colors = [NSArray arrayWithObjects:
                          [UIColor colorWithWhite:61/255.0 alpha:1],
                          [UIColor colorWithWhite:26/255.0 alpha:1],
                          nil];
            }
            else {
                colors = [NSArray arrayWithObjects:
                          [UIColor colorWithWhite:140/255.0 alpha:1],
                          [UIColor colorWithWhite:65/255.0 alpha:1],
                          nil];
            }
            aView.layer.cornerRadius = cornerRadius;
            [Util addGradientToLayer:aView.layer withColors:colors vertical:YES];
            views[i] = aView;
        }
        STButton* backButton = [[[STButton alloc] initWithFrame:buttonFrame normalView:views[0] activeView:views[1] target:self andAction:@selector(backButtonClicked:)] autorelease];
        [backButton addSubview:backIconView];
        width += backButton.frame.size.width + padding;
        backButton.layer.cornerRadius = cornerRadius;
        backButton.layer.shadowColor = [UIColor colorWithWhite:64.0/255 alpha:1].CGColor;
        backButton.layer.shadowRadius = 0;
        backButton.layer.shadowOpacity = 1;
        backButton.layer.shadowOffset = CGSizeMake(0, 1);
        [outputArray addObject:backButton];
    }
    for (STConsumptionToolbarItem* child in item.children) {
        UIImage* childIcon = [Util gradientImage:child.icon withPrimaryColor:@"404040" secondary:@"1a1a1a" andStyle:STGradientStyleVertical];
        STButton* button = [self consumptionButtonWithName:child.name icon:childIcon selector:@selector(childChosen:)];
        button.message = child;
        [Util reframeView:button withDeltas:CGRectMake(width, 0, 0, 0)];
        width += button.frame.size.width + padding;
        [outputArray addObject:button];
    }
    return width;
}

- (void)updateWithItem:(STConsumptionToolbarItem*)item animated:(BOOL)animated {
    STConsumptionToolbarItem* old = self.currentItem;
    self.currentItem = item;
    void (^mainBlock)(BOOL) = ^(BOOL finished) {
        if (self.currentViews) {
            for (UIView* view in self.currentViews) {
                [view removeFromSuperview];
            }
        }
        NSMutableArray* newViews = [NSMutableArray array];
        CGFloat width = [self generateViewsWithItem:item andOuput:newViews];
        self.currentViews = newViews;
        if (self.currentViews) {
            for (UIView* view in self.currentViews) {
                [Util reframeView:view withDeltas:CGRectMake(-width, 10, 0, 0)];
                [self.toolbarContents addSubview:view];
            }
            void (^block)(void) = ^{
                for (UIView* view in self.currentViews) {
                    [Util reframeView:view withDeltas:CGRectMake(width + 10, 0, 0, 0)];
                }
            };
            if (animated) {
                [UIView animateWithDuration:.25 animations:block];
            }
            else {
                block();
            }
        }
    };
    if (self.currentViews && animated) {
        [UIView animateWithDuration:.25 animations:^{
            for (UIView* view in self.currentViews) {
                [Util reframeView:view withDeltas:CGRectMake(0, self.frame.size.height + 5, 0, 0)];
            }
        } completion:mainBlock];
    }
    else {
        mainBlock(YES);
    }
    [self.delegate toolbar:self didMoveToItem:self.currentItem from:old];
}

+ (void)setupConfigurations {    
    [STConfiguration addNumber:[NSNumber numberWithFloat:33] forKey:_buttonHeightKey];
    [STConfiguration addNumber:[NSNumber numberWithFloat:5] forKey:_buttonPaddingKey];
    [STConfiguration addNumber:[NSNumber numberWithFloat:5] forKey:_buttonInnerPaddingKey];
    [STConfiguration addNumber:[NSNumber numberWithFloat:5] forKey:_buttonCornerRadiusKey];
}

@end
