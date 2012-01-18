//
//  TodoTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "TodoTableViewCell.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Favorite.h"
#import "Notifications.h"
#import "Stamp.h"
#import "UIColor+Stamped.h"
#import "User.h"
#import "Util.h"

static NSString* const kTitleFontString = @"TitlingGothicFBComp-Light";
static NSString* const kEllipsisFontString = @"TitlingGothicFBComp-Regular";
static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static const CGFloat kTitleMaxWidth = 214.0;
static const CGFloat kTitleFontSize = 47.0;
static const CGFloat kSubstringFontSize = 12.0;

@interface TodoTableViewCell ()
- (void)invertColors;
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (void)setupViews;
- (void)currentUserChanged:(NSNotification*)notification;

@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) UIImageView* completedImageView;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, readonly) CATextLayer* titleLayer;
@property (nonatomic, readonly) UIImageView* disclosureImageView;
@property (nonatomic, readonly) UIImageView* typeImageView;
@property (nonatomic, readonly) UILabel* descriptionLabel;

@property (nonatomic, assign) BOOL inButtonPhase;
@end

@implementation TodoTableViewCell

@synthesize favorite = favorite_;
@synthesize stampImageView = stampImageView_;
@synthesize completedImageView = completedImageView_;
@synthesize title = title_;
@synthesize titleLayer = titleLayer_;
@synthesize disclosureImageView = disclosureImageView_;
@synthesize typeImageView = typeImageView_;
@synthesize descriptionLabel = descriptionLabel_;
@synthesize inButtonPhase = inButtonPhase_;
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
  self.favorite = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  CGSize imageSize = typeImageView_.image.size;
  typeImageView_.frame = CGRectMake(CGRectGetMinX(titleLayer_.frame) + 1, 58, imageSize.width, imageSize.height);
  CGSize descriptionSize = [descriptionLabel_ sizeThatFits:CGSizeMake(200, MAXFLOAT)];
  descriptionLabel_.frame = CGRectMake(CGRectGetMaxX(typeImageView_.frame) + 4,
                                       CGRectGetMinY(typeImageView_.frame) - 2,
                                       descriptionSize.width,
                                       descriptionSize.height);
}

- (void)invertColors {
  if (!favorite_)
    return;
  UIColor* titleColor = (self.selected || self.highlighted) ? [UIColor whiteColor] : [UIColor stampedDarkGrayColor]; 
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  titleLayer_.string = [self titleAttributedStringWithColor:titleColor];
  titleLayer_.foregroundColor = titleColor.CGColor;
  [CATransaction commit];
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

- (void)prepareForReuse {
  self.favorite = nil;
  [super prepareForReuse];
}

- (void)setFavorite:(Favorite*)favorite {
  if (favorite) {
    stampImageView_.hidden = [favorite.complete boolValue];
    completedImageView_.hidden = ![favorite.complete boolValue];
  }
  
  if (favorite_ != favorite) {
    [favorite_ release];
    favorite_ = [favorite retain];

    if (favorite) {
      stampImageView_.hidden = [favorite.complete boolValue];
      completedImageView_.hidden = ![favorite.complete boolValue];
      self.title = favorite.entityObject.title;
      titleLayer_.string = [self titleAttributedStringWithColor:[UIColor stampedDarkGrayColor]];
      typeImageView_.image = favorite.entityObject.inboxTodoCategoryImage;
      typeImageView_.highlightedImage = favorite.entityObject.highlightedInboxTodoCategoryImage;
      descriptionLabel_.text = favorite.entityObject.subtitle;
      
      [self setNeedsDisplay];
    }
  }
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
  [self.contentView addSubview:disclosureImageView_];
  [disclosureImageView_ release];
  
  UIImage* stampImage = [UIImage imageNamed:@"stamp_42pt_strokePlus"];
  UIImage* highlightedImage = [Util whiteMaskedImageUsingImage:stampImage];
  stampImageView_ = [[UIImageView alloc] initWithImage:stampImage highlightedImage:highlightedImage];
  stampImageView_.frame = CGRectOffset(stampImageView_.frame, 12, 8);
  stampImageView_.hidden = [favorite_.complete boolValue];
  [self.contentView addSubview:stampImageView_];
  [stampImageView_ release];

  completedImageView_ = [[UIImageView alloc] initWithFrame:stampImageView_.frame];
  completedImageView_.hidden = ![favorite_.complete boolValue];
  completedImageView_.image = [[AccountManager sharedManager].currentUser stampImageWithSize:StampImageSize42];
  completedImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:completedImageView_.image];
  [self.contentView addSubview:completedImageView_];
  [completedImageView_ release];

  titleLayer_ = [[CATextLayer alloc] init];
  titleLayer_.truncationMode = kCATruncationEnd;
  titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
  titleLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
  titleLayer_.font = CTFontCreateWithName((CFStringRef)kEllipsisFontString, 0, NULL);  // So the ellipsis draws the way we like it.
  titleLayer_.fontSize = 24.0;
  titleLayer_.frame = CGRectMake(CGRectGetMaxX(stampImageView_.frame) + 14,
                                 10, kTitleMaxWidth, kTitleFontSize);
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
  
  typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectZero];
  typeImageView_.contentMode = UIViewContentModeLeft;
  [self.contentView addSubview:typeImageView_];
  [typeImageView_ release];
  
  descriptionLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  descriptionLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
  descriptionLabel_.textColor = [UIColor stampedGrayColor];
  descriptionLabel_.highlightedTextColor = [UIColor whiteColor];
  [self.contentView addSubview:descriptionLabel_];
  [descriptionLabel_ release];
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(stampImageView_.frame, [touch locationInView:self.contentView])) {
    inButtonPhase_ = YES;
    return;
  }
  [super touchesBegan:touches withEvent:event];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  inButtonPhase_ = NO;
  [super touchesCancelled:touches withEvent:event];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  if (inButtonPhase_) {
    if (!stampImageView_.hidden) {
      [delegate_ todoTableViewCell:self shouldStampEntity:favorite_.entityObject];
    } else {
      NSString* userID = [AccountManager sharedManager].currentUser.userID;
      NSString* entityID = favorite_.entityObject.entityID;
      NSPredicate* p =
          [NSPredicate predicateWithFormat:@"user.userID == %@ AND entityObject.entityID == %@", userID, entityID];
      Stamp* s = [Stamp objectWithPredicate:p];
      if (s)
        [delegate_ todoTableViewCell:self shouldShowStamp:s];
    }
    inButtonPhase_ = NO;
    return;
  }
  [super touchesEnded:touches withEvent:event];
}

- (void)currentUserChanged:(NSNotification*)notification {
  completedImageView_.image = [[AccountManager sharedManager].currentUser stampImageWithSize:StampImageSize42];
}


@end