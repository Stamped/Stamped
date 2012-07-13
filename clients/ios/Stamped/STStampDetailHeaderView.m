//
//  STStampDetailHeaderView.m
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailHeaderView.h"

#import <QuartzCore/QuartzCore.h>

#import <CoreText/CoreText.h>

#import "STStamp.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STButton.h"

@interface STStampDetailHeaderView ()

- (void)clicked:(id)msg;

@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readonly, retain) id<STEntity> entity;

@end

@implementation STStampDetailHeaderView

@synthesize stamp = _stamp;
@synthesize entity = entity_;

- (void)commonInit {
    UIView* views[2];
    for (NSInteger i = 0; i < 2; i++) {
        UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 64)] autorelease];
        UIImage* stampImage;
        UIImage* arrowImage;
        UIColor* titleColor;
        UIColor* subtitleColor;
        UIImage* categoryImage = [Util categoryIconForCategory:_stamp.entity.category
                                                   subcategory:_stamp.entity.subcategory
                                                        filter:nil
                                                       andSize:STCategoryIconSize9];
        
        if (i == 0) {
            arrowImage = [UIImage imageNamed:@"TEMP_eDetailBox_arrow_right"];
            stampImage = [Util stampImageForUser:self.stamp.user withSize:STStampImageSize42];
            titleColor = [UIColor stampedBlackColor];
            subtitleColor = [UIColor stampedGrayColor];
            view.backgroundColor = [UIColor clearColor];
            categoryImage = [Util gradientImage:categoryImage withPrimaryColor:@"b2b2b2" secondary:@"b2b2b2" andStyle:STGradientStyleVertical];
        }
        else {
            arrowImage = [UIImage imageNamed:@"TEMP_eDetailBox_arrow_right"];
            stampImage = [Util invertedStampImageForUser:self.stamp.user withSize:STStampImageSize42];
            titleColor = [UIColor whiteColor];
            subtitleColor = [UIColor whiteColor];
            [Util addGradientToLayer:view.layer withColors:[UIColor stampedBlueGradient] vertical:YES];
            categoryImage = [Util whiteMaskedImageUsingImage:categoryImage];
        }
        
        UIFont* titleFont = [UIFont stampedTitleFontWithSize:32];
        UILabel* titleView = [Util viewWithText:self.entity.title
                                           font:titleFont
                                          color:titleColor 
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(270, titleFont.lineHeight)];
        [Util reframeView:titleView withDeltas:CGRectMake(13,
                                                          36 - titleFont.ascender,
                                                          0, 0)];
        [view addSubview:titleView];
        
        UIFont* subtitleFont = [UIFont stampedFontWithSize:12];
        UIView* subtitleView = [Util viewWithText:self.entity.subtitle
                                             font:subtitleFont
                                            color:subtitleColor
                                             mode:UILineBreakModeTailTruncation
                                       andMaxSize:CGSizeMake(270, subtitleFont.lineHeight)];
        [Util reframeView:subtitleView withDeltas:CGRectMake(31,
                                                             52 - subtitleFont.ascender,
                                                             0, 0)];
        [view addSubview:subtitleView];
        
        
        UIImageView* categoryView = [[[UIImageView alloc] initWithImage:categoryImage] autorelease];
        [Util reframeView:categoryView withDeltas:CGRectMake(15,
                                                             43,
                                                             0, 0)];
        [view addSubview:categoryView];
        
        UIImageView* stampView = [[[UIImageView alloc] initWithImage:stampImage] autorelease];
        [Util reframeView:stampView withDeltas:CGRectMake(CGRectGetMaxX(titleView.frame) - 10, 
                                                          -10,
                                                          0, 0)];
        [view addSubview:stampView];
        
        UIImageView* arrowView = [[[UIImageView alloc] initWithImage:arrowImage] autorelease];
        [Util reframeView:arrowView withDeltas:CGRectMake(297,
                                                          24,
                                                          3, 4)];
        [view addSubview:arrowView];
        view.clipsToBounds = YES;
        views[i] = view;
    }
    STButton* button = [[[STButton alloc] initWithFrame:views[0].frame 
                                             normalView:views[0] 
                                             activeView:views[1] 
                                                 target:self 
                                              andAction:@selector(clicked:)] autorelease];
    [self addSubview:button];
}

- (id)initWithStamp:(id<STStamp>)stamp {
    self = [super initWithFrame:CGRectMake(0, 0, 320, 64)];
    if (self) {
        _stamp = [stamp retain];
        entity_ = [stamp.entity retain];
        [self commonInit];
    }
    return self;
}

- (id)initWithEntity:(id<STEntity>)entity {
    self = [super initWithFrame:CGRectMake(0, 0, 320, 64)];
    if (self) {
        entity_ = [entity retain];
        [self commonInit];
    }
    return self;
}

- (void)dealloc {
    [_stamp release];
    [entity_ release];
    [super dealloc];
}

- (void)clicked:(id)msg {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:self.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

@end
