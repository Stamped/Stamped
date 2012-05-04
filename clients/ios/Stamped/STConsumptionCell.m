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

@interface STConsumptionCellPreparation : NSObject <STCancellationDelegate>

- (id)initWithStamp:(id<STStamp>)stamp andCallback:(void(^)(NSError*, STCancellation*))block;
- (void)handleDetail:(id<STEntityDetail>)detail withError:(NSError*)error;

@property (nonatomic, readwrite, copy) void (^block)(NSError*, STCancellation*);
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readwrite, retain) STCancellation* detailCancellation;
@property (nonatomic, readwrite, retain) STCancellation* imageCancellation;

@end

@implementation STConsumptionCellPreparation 

@synthesize cancellation = cancellation_;
@synthesize detailCancellation = detailCancellation_;
@synthesize imageCancellation = imageCancellation_;
@synthesize block = block_;

- (id)initWithStamp:(id<STStamp>)stamp andCallback:(void(^)(NSError*, STCancellation*))block
{
  self = [super init];
  if (self) {
    [self retain];
    self.block = block;
    self.cancellation = [STCancellation cancellationWithDelegate:self];
    self.detailCancellation = [[STStampedAPI sharedInstance] entityDetailForEntityID:stamp.entity.entityID
                                                                         andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
                                                                           [self handleDetail:detail withError:error];
                                                                         }];
  }
  return self;
}

- (void)dealloc
{
  cancellation_.delegate = nil;
  [cancellation_ release];
  [detailCancellation_ cancel];
  [detailCancellation_ release];
  [imageCancellation_ cancel];
  [imageCancellation_ release];
  self.block = nil;
  [super dealloc];
}

- (void)handleDetail:(id<STEntityDetail>)detail withError:(NSError*)error {
  NSAssert1(!self.cancellation.cancelled, @"Should not have received detail if cancelled: %@", detail.title);
  BOOL finish = YES;
  if (detail) {
    NSString* url = [Util entityImageURLForEntityDetail:detail];
    if (url) {
      finish = NO;
      self.imageCancellation = [[STImageCache sharedInstance] imageForImageURL:url andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
        if (self.block) {
          self.cancellation.delegate = nil;
          self.block(error, self.cancellation);
          [self autorelease];
        }
      }];
    }
  }
  if (finish && self.block) {
    self.cancellation.delegate = nil;
    self.block(error, self.cancellation);
    [self autorelease];
  }
}

- (void)cancellationWasCancelled:(STCancellation*)cancellation {
  [detailCancellation_ cancel];
  [imageCancellation_ cancel];
  [self autorelease];
}

@end

@interface STConsumptionCell ()

- (void)handleEntityDetail:(id<STEntityDetail>)entityDetail andError:(NSError*)error;

@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readonly, retain) UIActivityIndicatorView* activityView;
@property (nonatomic, readonly, retain) id<STEntityDetail> entityDetail;
@property (nonatomic, readonly, retain) STCancellation* entityDetailCancellation;
@property (nonatomic, readwrite, retain) STCancellation* entityImageCancellation;
@property (nonatomic, readonly, assign) CGFloat imageHeight;
@property (nonatomic, readonly, assign) CGFloat imageYOffset;

@end

@implementation STConsumptionCell

@synthesize stamp = stamp_;
@synthesize activityView = activityView_;
@synthesize entityDetail = entityDetail_;
@synthesize entityDetailCancellation = entityDetailCancellation_;
@synthesize entityImageCancellation = entityImageCancellation_;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
  if (self) {
    stamp_ = [stamp retain];
    self.frame = CGRectMake(0, 0, 320, [STConsumptionCell cellHeightForStamp:stamp]);
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
    rightButton.message = stamp;
    UIImageView* rightArrow = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"disclosure_arrow"]] autorelease];
    rightArrow.frame = [Util centeredAndBounded:rightArrow.frame.size inFrame:rightHitTargetFrame];
    [rightButton addSubview:rightArrow];
    [Util reframeView:rightButton withDeltas:CGRectMake(260 - 16, (self.imageYOffset + self.imageHeight / 2) - 16 - rightArrow.frame.size.height / 2, 0, 0)];
    [self addSubview:rightButton];
    
    CGFloat imageMax = self.imageHeight + self.imageYOffset;
    CGFloat previewHeight = [STPreviewsView previewHeightForStamp:stamp andMaxRows:1];
    CGFloat textYOffset = imageMax + 15;
    if (previewHeight > 0) {
      CGRect previewFrame = CGRectMake(0, imageMax+12, 320, previewHeight);
      STPreviewsView* previewsView = [[[STPreviewsView alloc] initWithStamp:stamp andMaxRows:1] autorelease];
      previewsView.frame = [Util centeredAndBounded:previewsView.frame.size inFrame:previewFrame];
      [self addSubview:previewsView];
      textYOffset = CGRectGetMaxY(previewsView.frame) + 5;
    }
    
    CGFloat maxTextWidth = 300;
    CGFloat maxTitleWidth = 200;
    UIFont* titleFont = [UIFont stampedBoldFontWithSize:10];
    UIColor* textColor = [UIColor stampedGrayColor];
    UIView* titleView = [Util viewWithText:stamp.entity.title
                                      font:titleFont
                                     color:textColor
                                      mode:UILineBreakModeTailTruncation
                                andMaxSize:CGSizeMake(maxTitleWidth, [Util lineHeightForFont:titleFont])];
    UIFont* subtitleFont = [UIFont stampedFontWithSize:10];
    UIView* subtitleView = [Util viewWithText:[NSString stringWithFormat:@" - %@", stamp.entity.subtitle]
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
    
    [Util addGradientToLayer:self.layer withColors:[UIColor stampedLightGradient] vertical:YES];
    
    __block STConsumptionCell* weakSelf = self;
    entityDetailCancellation_ = [[[STStampedAPI sharedInstance] entityDetailForEntityID:stamp.entity.entityID
                                                                            andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
                                                                              [weakSelf handleEntityDetail:detail andError:error];
                                                                            }] retain];
  }
  return self;
}

- (void)rightButtonClicked:(id<STStamp>)stamp {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:stamp.entity.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)dealloc
{
  [stamp_ release];
  [activityView_ release];
  [entityDetail_ release];
  [entityDetailCancellation_ cancel];
  [entityDetailCancellation_ release];
  [entityImageCancellation_ cancel];
  [entityImageCancellation_ release];
  [super dealloc];
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
    imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:imageBounds];
    imageView.layer.shadowOpacity = .5;
    imageView.layer.shadowColor = [UIColor blackColor].CGColor;
    imageView.layer.shadowRadius = 7;
    imageView.layer.shadowOffset = CGSizeMake(0, imageView.layer.shadowRadius/2);
    [self addSubview:imageView];
    UIImageView* stampImage = [[[UIImageView alloc] initWithImage:[Util stampImageForUser:self.stamp.user withSize:STStampImageSize46]] autorelease];
    [Util reframeView:stampImage withDeltas:CGRectMake(CGRectGetMaxX(imageView.frame) - 40,
                                                       imageView.frame.origin.y - 8,
                                                       0,
                                                       0)];
    [self addSubview:stampImage];
  }
  else {
    [STDebug log:@"Failed to load entity image"];
  }
}

- (void)handleEntityDetail:(id<STEntityDetail>)entityDetail andError:(NSError*)error {
  [self.activityView stopAnimating];
  if ([Util entityImageURLForEntityDetail:entityDetail]) {
    self.entityImageCancellation = [[STImageCache sharedInstance] entityImageForEntityDetail:entityDetail andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
      [self handleImage:image withError:error];
    }];
  }
  else {
    [self handleImage:[UIImage imageNamed:@"TEMP_noImage"] withError:nil];
  }
  
}

+ (CGFloat)cellHeightForStamp:(id<STStamp>)stamp {
  if ([stamp.entity.category isEqualToString:@"music"]) {
    return 270;
  }
  return 310;
}

- (CGFloat)imageHeight {
  if ([self.stamp.entity.category isEqualToString:@"music"]) {
    return 180;
  }
  return 225;
}

- (CGFloat)imageYOffset {
  return 12;
}

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError*, STCancellation*))block {
  STConsumptionCellPreparation* prep = [[[STConsumptionCellPreparation alloc] initWithStamp:stamp andCallback:block] autorelease];
  return prep.cancellation;
}

@end