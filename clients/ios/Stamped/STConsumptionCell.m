//
//  STConsumptionCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionCell.h"
#import "STStampedAPI.h"
#import <QuartzCore/QuartzCore.h>
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STImageCache.h"
#import "STDebug.h"
#import "STPreviewsView.h"
#import "STSimplePreviews.h"
#import "STSimpleStamp.h"

@interface STConsumptionCell ()

@property (nonatomic, readonly, retain) UIActivityIndicatorView* activityView;
@property (nonatomic, readonly, retain) id<STEntityDetail> entityDetail;
@property (nonatomic, readwrite, retain) STCancellation* entityImageCancellation;
@property (nonatomic, readonly, assign) CGFloat imageHeight;
@property (nonatomic, readonly, assign) CGFloat imageYOffset;
@property (nonatomic, readwrite, retain) UIView* imageView;

@end

@implementation STConsumptionCell

@synthesize activityView = activityView_;
@synthesize entityDetail = entityDetail_;
@synthesize entityImageCancellation = entityImageCancellation_;
@synthesize imageView = imageView_;

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
    if (self) {
        entityDetail_ = [entityDetail retain];
        self.frame = CGRectMake(0, 0, 320, [STConsumptionCell cellHeightForEntityDetail:entityDetail_]);
        self.accessoryType = UITableViewCellAccessoryNone;
        self.selectionStyle = UITableViewCellSelectionStyleNone;
        activityView_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
        activityView_.frame = self.frame;
        [self addSubview:activityView_];
        [activityView_ startAnimating];
        
        UIView* rightButtonViews[2];
        CGRect rightButtonFrame = CGRectMake(0, 0, 32, 32);
        CGRect rightHitTargetFrame = CGRectMake(0, 0, 64, 64);
        for (NSInteger i = 0; i < 2; i++) {
            UIView* buttonView = [[[UIView alloc] initWithFrame:rightButtonFrame] autorelease];
            buttonView.layer.cornerRadius = buttonView.frame.size.width / 2;
            NSArray* gradient;
            UIColor* borderColor;
            if (i == 0) {
                gradient = [UIColor stampedLightGradient];
                borderColor = [UIColor stampedLightGrayColor];
            }
            else {
                gradient = [UIColor stampedDarkGradient];
                borderColor = [UIColor stampedGrayColor];
            }
            buttonView.layer.borderColor = borderColor.CGColor;
            buttonView.layer.borderWidth = 1;
            buttonView.layer.shadowColor = [UIColor whiteColor].CGColor;
            buttonView.layer.shadowOpacity = 1;
            buttonView.layer.shadowOffset = CGSizeMake(0, 2);
            buttonView.layer.shadowRadius = 2;
            [Util addGradientToLayer:buttonView.layer withColors:gradient vertical:YES];
            buttonView.frame = [Util centeredAndBounded:buttonView.frame.size inFrame:rightHitTargetFrame];
            rightButtonViews[i] = buttonView;
        }
        STButton* rightButton = [[[STButton alloc] initWithFrame:rightHitTargetFrame
                                                      normalView:rightButtonViews[0] 
                                                      activeView:rightButtonViews[1]
                                                          target:self
                                                       andAction:@selector(rightButtonClicked:)] autorelease];
        rightButton.message = entityDetail;
        UIImageView* rightArrow = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"disclosure_arrow"]] autorelease];
        rightArrow.frame = [Util centeredAndBounded:rightArrow.frame.size inFrame:rightHitTargetFrame];
        [rightButton addSubview:rightArrow];
        [Util reframeView:rightButton withDeltas:CGRectMake(260 - 16, (self.imageYOffset + self.imageHeight / 2) - 16 - rightArrow.frame.size.height / 2, 0, 0)];
        [self addSubview:rightButton];
        
        CGFloat imageMax = self.imageHeight + self.imageYOffset;
        CGFloat previewHeight = [STPreviewsView previewHeightForPreviews:entityDetail_.previews andMaxRows:1];
        CGRect previewFrame = CGRectMake(0, imageMax+12, 320, previewHeight);
        STPreviewsView* previewsView = [[[STPreviewsView alloc] initWithFrame:CGRectZero] autorelease];
        [previewsView setupWithPreview:entityDetail_.previews maxRows:1];
        previewsView.frame = [Util centeredAndBounded:previewsView.frame.size inFrame:previewFrame];
        [self addSubview:previewsView];
        CGFloat textYOffset = CGRectGetMaxY(previewsView.frame) + 5;
        
        CGFloat maxTextWidth = 300;
        CGFloat maxTitleWidth = 200;
        UIFont* titleFont = [UIFont stampedBoldFontWithSize:12];
        UIColor* textColor = [UIColor stampedGrayColor];
        UIView* titleView = [Util viewWithText:entityDetail_.title
                                          font:titleFont
                                         color:textColor
                                          mode:UILineBreakModeTailTruncation
                                    andMaxSize:CGSizeMake(maxTitleWidth, [Util lineHeightForFont:titleFont])];
        UIFont* subtitleFont = [UIFont stampedFontWithSize:12];
        UIView* subtitleView = [Util viewWithText:[NSString stringWithFormat:@" - %@", entityDetail_.subtitle]
                                             font:subtitleFont
                                            color:textColor
                                             mode:UILineBreakModeTailTruncation
                                       andMaxSize:CGSizeMake(maxTextWidth - titleView.frame.size.width, [Util lineHeightForFont:subtitleFont])];
        CGSize combinedSize = CGSizeMake(titleView.frame.size.width + subtitleView.frame.size.width, MAX(titleView.frame.size.height, subtitleView.frame.size.height));
        CGRect textFrame = [Util centeredAndBounded:combinedSize inFrame:CGRectMake(0, textYOffset, 320, combinedSize.height)];
        [Util reframeView:titleView withDeltas:CGRectMake(textFrame.origin.x, textFrame.origin.y, 0, 0)];
        [Util reframeView:subtitleView withDeltas:CGRectMake(CGRectGetMaxX(titleView.frame), textFrame.origin.y, 0, 0)];
        [self addSubview:titleView];
        [self addSubview:subtitleView];
        
        //[Util addGradientToLayer:self.layer withColors:[UIColor stampedLightGradient] vertical:YES];
        
        NSString* imageURL = [Util entityImageURLForEntity:self.entityDetail];
        if (imageURL) {
            UIImage* image = [[STImageCache sharedInstance] cachedImageForImageURL:imageURL];
            if (image) {
                [self handleImage:image withError:nil];
            }
            else {
                self.entityImageCancellation = [[STImageCache sharedInstance] imageForImageURL:imageURL
                                                                                   andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                                                                                       [self handleImage:image withError:error];
                                                                                   }];
            }
        }
        else {
            [self handleImage:[UIImage imageNamed:@"TEMP_noImage"] withError:nil];
        }
    }
    return self;
}

- (void)rightButtonClicked:(id)notImportant {
    STActionContext* context = [STActionContext context];
    context.entityDetail = self.entityDetail;
    id<STAction> action = [STStampedActions actionViewEntity:self.entityDetail.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)dealloc {
    [activityView_ release];
    [entityDetail_ release];
    [entityImageCancellation_ cancel];
    [entityImageCancellation_ release];
    [imageView_ release];
    [super dealloc];
}

- (void)handleCombo {
    BOOL addedAction = NO;
    if (self.entityDetail.actions.count > 0 && [self.entityDetail.category isEqualToString:@"music"]) {
        id<STActionItem> actionItem = [self.entityDetail.actions objectAtIndex:0];
        id<STAction> action = [actionItem action];
        if (action) {
            STActionContext* context = [STActionContext context];
            context.entity = self.entityDetail;
            if ([[STActionManager sharedActionManager] canHandleAction:action withContext:context]) {
                UIView* buttonViews[2];
                CGRect buttonFrame = CGRectMake(0, 0, 60, 60);
                for (NSInteger i = 0; i < 2; i++) {
                    UIView* view = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
                    view.layer.cornerRadius = view.frame.size.width / 2;
                    view.layer.borderWidth = 2;
                    view.layer.borderColor = [UIColor colorWithWhite:.1 alpha:.4].CGColor;
                    UIColor* backgroundColor;
                    if (i == 0) {
                        backgroundColor = [UIColor colorWithWhite:1 alpha:.7];
                    }
                    else {
                        backgroundColor = [UIColor colorWithWhite:.7 alpha:.7];
                    }
                    view.backgroundColor = backgroundColor;
                    buttonViews[i] = view;
                }
                STButton* button = [[[STButton alloc] initWithFrame:buttonFrame 
                                                         normalView:buttonViews[0]
                                                         activeView:buttonViews[1]
                                                             target:self
                                                          andAction:@selector(actionButtonClicked:)] autorelease];
                button.message = action;
                UIImageView* playView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"TEMP_play_button"]] autorelease];
                playView.frame = [Util centeredAndBounded:playView.frame.size inFrame:button.frame];
                [Util reframeView:playView withDeltas:CGRectMake(4, 0, 0, 0)];
                [button addSubview:playView];
                button.frame = [Util centeredAndBounded:button.frame.size inFrame:self.imageView.frame];
                [self addSubview:button];
                addedAction = YES;
            }
        }
    }
    if (!addedAction) {
        UIView* views[2];
        for (NSInteger i = 0; i < 2; i++) {
            UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.imageView.frame.size.width, self.imageView.frame.size.height)] autorelease];
            if (i == 0) {
                view.hidden = YES;
                view.userInteractionEnabled = NO;
            }
            else {
                [Util addGradientToLayer:view.layer 
                              withColors:[NSArray arrayWithObjects:[UIColor colorWithWhite:.3 alpha:.5], [UIColor colorWithWhite:.2 alpha:.7], nil]
                                vertical:YES];
            }
            views[i] = view;
        }
        STButton* button = [[[STButton alloc] initWithFrame:self.imageView.frame
                                                 normalView:views[0]
                                                 activeView:views[1]
                                                     target:self 
                                                  andAction:@selector(rightButtonClicked:)] autorelease];
        [self addSubview:button];
    }
}

- (void)handleImage:(UIImage*)image withError:(NSError*)error {
    if (image) {
        CGRect imageBounds = CGRectMake(70, self.imageYOffset, 180, self.imageHeight);
        UIImageView* imageView = [[[UIImageView alloc] initWithImage:image] autorelease];
        BOOL shouldShrink;
        if (image.size.width < 300 && image.size.height < 400) {
            shouldShrink = NO;
        }
        else {
            shouldShrink = YES;
        }
        if (shouldShrink) {
            CGSize newSize = [Util size:imageView.frame.size withScale:[Util legacyImageScale]];
            imageView.frame = CGRectMake(0, 0, newSize.width, newSize.height);
        }
        [self.activityView stopAnimating];
        self.activityView.hidden = YES;
        imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:imageBounds];
        imageView.layer.shadowOpacity = .5;
        imageView.layer.shadowColor = [UIColor blackColor].CGColor;
        imageView.layer.shadowRadius = 7;
        imageView.layer.shadowOffset = CGSizeMake(0, imageView.layer.shadowRadius/2);
        imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;
        [self addSubview:imageView];
        /*
         UIImageView* stampImage = [[[UIImageView alloc] initWithImage:[Util stampImageForUser:self.stamp.user withSize:STStampImageSize46]] autorelease];
         [Util reframeView:stampImage withDeltas:CGRectMake(CGRectGetMaxX(imageView.frame) - 40,
         imageView.frame.origin.y - 8,
         0,
         0)];
         [self addSubview:stampImage];
         */
        self.imageView = imageView;
        if (self.entityDetail) {
            [self handleCombo];
        }
    }
    else {
        [self handleImage:[UIImage imageNamed:@"TEMP_noImage"] withError:nil];
        [STDebug log:@"Failed to load entity image"];
    }
}

- (void)actionButtonClicked:(id<STAction>)action {
    
    STActionContext* context = [STActionContext context];
    context.entity = self.entityDetail;
    context.entityDetail = self.entityDetail;
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)handleEntityDetail:(id<STEntityDetail>)entityDetail andError:(NSError*)error {
    [self.activityView stopAnimating];
    //NSLog(@"array:%@",entityDetail.images);
    entityDetail_ = [entityDetail retain];
    if (self.imageView) {
        [self handleCombo];
    }
}

+ (CGFloat)cellHeightForEntityDetail:(id<STEntityDetail>)entityDetail {
    if ([entityDetail.category isEqualToString:@"music"]) {
        return 275;
    }
    return 315;
}

- (CGFloat)imageHeight {
    if ([self.entityDetail.category isEqualToString:@"music"]) {
        return 180;
    }
    return 225;
}

- (CGFloat)imageYOffset {
    return 12;
}

+ (STCancellation*)prepareForEntityDetail:(id<STEntityDetail>)entityDetail
                             withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
    NSMutableArray* images = [NSMutableArray array];
    NSString* bigImage = [Util entityImageURLForEntity:entityDetail];
    if (bigImage) {
        [images addObject:bigImage];
    }
    [images addObjectsFromArray:[STPreviewsView imagesForPreviewWithPreviews:entityDetail.previews andMaxRows:1]];
    return [STCancellation loadImages:images withCallback:block];
    //STConsumptionCellPreparation* prep = [[[STConsumptionCellPreparation alloc] initWithStamp:stamp andCallback:block] autorelease];
    //return prep.cancellation;
}

@end
