//
//  TodoTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "TodoTableViewCell.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Favorite.h"
#import "Notifications.h"
#import "UIColor+Stamped.h"
#import "User.h"
#import "Util.h"

static UIImage* kCompletedStamp = nil;

static NSString* const kTitleFontString = @"TGLight";
static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static const CGFloat kTitleMaxWidth = 210.0;
static const CGFloat kTitleFontSize = 47.0;
static const CGFloat kSubstringFontSize = 12.0;

@interface TodoTableViewCell ()
- (void)invertColors;
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (void)setupViews;
- (UIImage*)completedStamp;
- (void)currentUserChanged:(NSNotification*)notification;

@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) UIImageView* completedImageView;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, readonly) CATextLayer* titleLayer;
@property (nonatomic, readonly) UIImageView* disclosureImageView;
@property (nonatomic, readonly) UIImageView* typeImageView;
@property (nonatomic, readonly) UILabel* descriptionLabel;

@property (nonatomic, assign) BOOL inAddingPhase;
@end

@implementation TodoTableViewCell

@synthesize completed = completed_;
@synthesize entityObject = entityObject_;
@synthesize stampImageView = stampImageView_;
@synthesize completedImageView = completedImageView_;
@synthesize title = title_;
@synthesize titleLayer = titleLayer_;
@synthesize disclosureImageView = disclosureImageView_;
@synthesize typeImageView = typeImageView_;
@synthesize descriptionLabel = descriptionLabel_;
@synthesize inAddingPhase = inAddingPhase_;
@synthesize delegate = delegate_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    [self setupViews];
    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(currentUserChanged:) 
                                                 name:kCurrentUserHasUpdatedNotification 
                                               object:nil];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [titleAttributes_ release];
  CFRelease(titleFont_);
  CFRelease(titleStyle_);
  self.title = nil;
  self.entityObject = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)invertColors {
  UIColor* titleColor = (self.selected || self.highlighted) ? [UIColor whiteColor] : [UIColor stampedDarkGrayColor]; 
  titleLayer_.string = [self titleAttributedStringWithColor:titleColor];
  titleLayer_.foregroundColor = titleColor.CGColor;
  [self setNeedsDisplay];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [self invertColors];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
  [super setHighlighted:highlighted animated:animated];
  [self invertColors];
}

- (void)setEntityObject:(Entity*)entityObject {
  if (entityObject_ != entityObject) {
    [entityObject_ release];
    entityObject_ = [entityObject retain];
    
    if (entityObject) {
      self.title = entityObject.title;
      titleLayer_.string = [self titleAttributedStringWithColor:[UIColor stampedDarkGrayColor]];
      UIImage* typeImage = [entityObject categoryImage];
      typeImageView_.image = typeImage;
      typeImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:typeImage];
      descriptionLabel_.text = entityObject.subtitle;

      [self setNeedsDisplay];
    }
  }
}

- (void)setCompleted:(BOOL)completed {
  completed_ = completed;
  stampImageView_.hidden = completed;
  completedImageView_.hidden = !completed;
  [self setNeedsDisplay];
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  if (!title_)
    return nil;

  [titleAttributes_ setObject:(id)color.CGColor forKey:(id)kCTForegroundColorAttributeName];
  NSAttributedString* titleAttributedString =
      [[NSAttributedString alloc] initWithString:title_
                                      attributes:titleAttributes_];
  return [titleAttributedString autorelease];
}

- (void)setupViews {
  disclosureImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(300, 34, 8, 11)];
  disclosureImageView_.contentMode = UIViewContentModeScaleAspectFit;
  UIImage* disclosureArrowImage = [UIImage imageNamed:@"disclosure_arrow"];
  disclosureImageView_.image = disclosureArrowImage;
  disclosureImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureArrowImage];
  [self addSubview:disclosureImageView_];
  [disclosureImageView_ release];
  
  UIImage* stampImage = [UIImage imageNamed:@"stamp_42pt_strokePlus"];
  UIImage* highlightedImage = [Util whiteMaskedImageUsingImage:stampImage];
  stampImageView_ = [[UIImageView alloc] initWithImage:stampImage highlightedImage:highlightedImage];
  stampImageView_.frame = CGRectOffset(stampImageView_.frame, 14, 8);
  stampImageView_.hidden = completed_;
  [self.contentView addSubview:stampImageView_];
  [stampImageView_ release];

  completedImageView_ = [[UIImageView alloc] initWithFrame:stampImageView_.frame];
  completedImageView_.hidden = !completed_;
  completedImageView_.image = [self completedStamp];
  [self.contentView addSubview:completedImageView_];
  [completedImageView_ release];

  titleLayer_ = [[CATextLayer alloc] init];
  titleLayer_.truncationMode = kCATruncationEnd;
  titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
  titleLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
  titleLayer_.fontSize = 24.0;
  titleLayer_.frame = CGRectMake(CGRectGetMaxX(stampImageView_.frame) + 15,
                                 11, kTitleMaxWidth, kTitleFontSize);
  titleLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                    forKey:@"contents"];
  titleFont_ = CTFontCreateWithName((CFStringRef)kTitleFontString, kTitleFontSize, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  titleStyle_ = CTParagraphStyleCreate(settings, numSettings);
  titleAttributes_ = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
                      (id)titleFont_, (id)kCTFontAttributeName,
                      (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
                      (id)titleStyle_, (id)kCTParagraphStyleAttributeName,
                      (id)[NSNumber numberWithDouble:1.2], (id)kCTKernAttributeName, nil];
  [self.contentView.layer addSublayer:titleLayer_];
  [titleLayer_ release];
  
  typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(CGRectGetMaxX(stampImageView_.frame) + 15, 59, 15, 12)];
  typeImageView_.contentMode = UIViewContentModeScaleAspectFit;
  [self addSubview:typeImageView_];
  [typeImageView_ release];
  
  descriptionLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeImageView_.frame) + 3, 57, 200, 16)];
  descriptionLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
  descriptionLabel_.textColor = [UIColor stampedGrayColor];
  descriptionLabel_.highlightedTextColor = [UIColor whiteColor];
  [self.contentView addSubview:descriptionLabel_];
  [descriptionLabel_ release];
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];
  if (!stampImageView_.hidden &&
      CGRectContainsPoint(stampImageView_.frame, [touch locationInView:self.contentView])) {
    inAddingPhase_ = YES;
    return;
  }
  [super touchesBegan:touches withEvent:event];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  inAddingPhase_ = NO;
  [super touchesCancelled:touches withEvent:event];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  if (inAddingPhase_) {
    [delegate_ todoTableViewCell:self shouldStampEntity:entityObject_];
    inAddingPhase_ = NO;
    return;
  }
  [super touchesEnded:touches withEvent:event];
}

- (UIImage*)completedStamp {
  if (kCompletedStamp)
    return kCompletedStamp;
  
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser)
    return nil;

  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:currentUser.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (currentUser.secondaryColor) {
    [Util splitHexString:currentUser.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  UIImage* img = [UIImage imageNamed:@"stamp_42pt_texture"];
  CGFloat width = img.size.width;
  CGFloat height = img.size.height;
  
  UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();
  
  CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
  CGFloat colors[] = {r1, g1, b1, 1.0,  r2, g2, b2, 1.0};
  CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
  CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
  CGPoint gradientStartPoint = CGPointZero;
  CGPoint gradientEndPoint = CGPointMake(width, height);
  CGContextDrawLinearGradient(context,
                              gradientRef,
                              gradientStartPoint,
                              gradientEndPoint,
                              kCGGradientDrawsAfterEndLocation);
  CGGradientRelease(gradientRef);
  CGColorSpaceRelease(colorSpace);
  kCompletedStamp = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  return kCompletedStamp;
}

- (void)currentUserChanged:(NSNotification*)notification {
  completedImageView_.image = [self completedStamp];
}

@end
