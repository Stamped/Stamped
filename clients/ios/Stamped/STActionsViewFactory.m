//
//  STActionsViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionsViewFactory.h"
#import "STViewDelegate.h"
#import "STEntityDetail.h"
#import <QuartzCore/QuartzCore.h>
#import "STImageView.h"
#import "Util.h"
#import "STViewContainer.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"
#import "STImageCache.h"
#import "STActionManager.h"
#import "STConfiguration.h"
#import "STStampedActions.h"
#import "STSimpleActionItem.h"

@interface ActionItemView : STButton

- (id)initWithAction:(id<STActionItem>)action andFrame:(CGRect)frame delegate:(id<STViewDelegate>)delegate;
- (void)selected:(id)button;

@property (nonatomic, assign) id<STViewDelegate> delegate;
@property (nonatomic, retain) id<STActionItem> actionItem;
@property (nonatomic, retain) id<STEntityDetail> entityDetail;

@end

@implementation ActionItemView

@synthesize delegate = delegate_;
@synthesize actionItem = actionItem_;
@synthesize entityDetail = _entityDetail;


/*
 TODO
 Check Font
 
 */
- (id)initWithAction:(id<STActionItem>)action andFrame:(CGRect)frame delegate:(id<STViewDelegate>)delegate {
    UIView* views[2];
    CGRect childFrame = CGRectMake(0, 0, frame.size.width, frame.size.height);
    for (NSInteger i = 0; i < 2; i++) {
        UIView* view = [[[UIView alloc] initWithFrame:childFrame] autorelease];
        
        NSArray* gradient;
        UIColor* textColor;
        UIColor* borderColor;
        //UIColor* shadowColor;
        
        NSMutableArray* iconURLs = [NSMutableArray array];
        
        if (action.action.sources.count) {
            for (id<STSource> source in action.action.sources) {
                if (source.icon &&
                    ([STConfiguration flag:STActionManagerShowAllActionsKey] ||
                     [[STActionManager sharedActionManager] canHandleSource:source
                                                                  forAction:action.action.type
                                                                withContext:[STActionContext context]])) {
                         [iconURLs addObject:source.icon];
                     }
            }
        }
        
        if (i == 0) {
            gradient = [UIColor stampedLightGradient];
            textColor = [UIColor stampedDarkGrayColor];
            borderColor = [UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4];
        }
        else {
            gradient = [UIColor stampedButtonGradient];
            textColor = [UIColor whiteColor];
            borderColor = [UIColor whiteColor];
        }
        
        CGFloat iconsMinX = CGRectGetMaxX(childFrame);
        if (iconURLs.count) {
            NSInteger index = iconURLs.count - 1;
            CGFloat offset = childFrame.size.width - 32;
            while (index >= 0) {
                CGRect iconFrame = CGRectMake(offset, 14, 16, 16);
                iconsMinX = offset;
                UIImageView* iconView = [[[UIImageView alloc] initWithFrame:iconFrame] autorelease];
                [view addSubview:iconView];
                [[STImageCache sharedInstance] imageForImageURL:[iconURLs objectAtIndex:index] andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                    if (i == 1 && image) {
                        //image = [Util whiteMaskedImageUsingImage:image];
                    }
                    iconView.image = image;  
                }];
                offset -= 20;
                index--;
            }
        }
        view.layer.cornerRadius = 2.0;
        view.layer.borderColor = borderColor.CGColor;
        view.layer.borderWidth = 1.0;
        view.layer.shadowColor = [UIColor blackColor].CGColor;
        view.layer.shadowOpacity = .05;
        view.layer.shadowRadius = 1.0;
        view.layer.shadowOffset = CGSizeMake(0, 1);
        view.layer.shadowPath = [UIBezierPath bezierPathWithRect:view.bounds].CGPath;
        
        [Util addGradientToLayer:view.layer withColors:gradient vertical:YES];
        
        CGRect labelFrame = frame;
        labelFrame.size.width = 200;
        labelFrame.origin.x = 44;
        labelFrame.origin.y = 0;
        
        CGFloat labelX = 44;
        UIFont* labelFont = [UIFont stampedBoldFontWithSize:12];
        
        UIView* label = [Util viewWithText:action.name
                                      font:labelFont
                                     color:textColor
                                      mode:UILineBreakModeTailTruncation
                                andMaxSize:CGSizeMake(iconsMinX - labelX, CGFLOAT_MAX)];
        [Util reframeView:label withDeltas:CGRectMake(labelX,
                                                      25 - labelFont.ascender,
                                                      0, 0)];
        [view addSubview:label];
        
        if (action.icon) {
            CGRect imageFrame = CGRectMake(12, 12, 20, 20);
            UIImageView* imageView = [[[UIImageView alloc] initWithFrame:imageFrame] autorelease];
            [[STImageCache sharedInstance] imageForImageURL:action.icon andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                if (i == 1 && image) {
                    image = [Util whiteMaskedImageUsingImage:image];
                }
                imageView.image = image;
            }];
            [view addSubview:imageView];
        }
        views[i] = view;
    }
    self = [super initWithFrame:frame normalView:views[0] activeView:views[1] target:nil andAction:@selector(selected:)];
    self.target = self;
    if (self) {
        self.delegate = delegate;
        self.actionItem = action;
    }
    return self;
}

- (void)dealloc {
    self.action = nil;
    self.delegate = nil;
    [_entityDetail release];
    [super dealloc];
}

- (void)selected:(id)button {
    STActionContext* context = [STActionContext contextInView:self];
    context.entityDetail = self.entityDetail;
    [[STActionManager sharedActionManager] didChooseAction:self.actionItem.action withContext:context];
}

@end

@implementation STActionsViewFactory

- (UIView*)viewWithActions:(NSArray<STActionItem>*)actionItems
              entityDetail:(id<STEntityDetail>)detail
               andDelegate:(id<STViewDelegate>)delegate  {
    STViewContainer* view = nil;
    if (detail.actions) {
        view = [[[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 10)] autorelease];
        CGFloat cell_height = 44;
        CGFloat cell_padding_h = 5;
        CGFloat cell_width = 290;
        CGFloat cell_padding_w = (320 - cell_width) / 2.0;
        for (id<STActionItem> action in actionItems) {
            id<STAction> actualAction = action.action;
            STActionContext* context = [STActionContext context];
            context.entityDetail = detail;
            if ([STConfiguration flag:STActionManagerShowAllActionsKey] || 
                [[STActionManager sharedActionManager] canHandleAction:actualAction withContext:context]) {
                CGRect frame = CGRectMake(cell_padding_w, 0, cell_width, cell_height);
                ActionItemView* actionView = [[ActionItemView alloc] initWithAction:action andFrame:frame delegate:view]; 
                actionView.entityDetail = detail;
                [view appendChildView:actionView];
                [actionView release];
                CGRect viewFrame = view.frame;
                viewFrame.size.height += cell_padding_h;
                view.frame = viewFrame;
            }
        }
    }
    return view;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)detail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
    return [self viewWithActions:detail.actions entityDetail:detail andDelegate:delegate];
}

+ (UIView*)moreInformationEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate {
    STActionContext* context = [STActionContext context];
    context.entityDetail = entityDetail;
    id<STAction> action = [STStampedActions actionViewEntity:entityDetail.entityID withOutputContext:context];
    STSimpleActionItem* item = [[[STSimpleActionItem alloc] init] autorelease];
    item.action = action;
    item.name = @"View more information";
    STActionsViewFactory* factory = [[[STActionsViewFactory alloc] init] autorelease];
    return [factory viewWithActions:[NSArray arrayWithObject:item] entityDetail:entityDetail andDelegate:delegate];
}

@end
