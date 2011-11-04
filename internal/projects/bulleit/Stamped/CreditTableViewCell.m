//
//  CreditTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreditTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "AccountManager.h"

@interface CreditTableViewCell ()
- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color;

@property (nonatomic, readonly) UILabel* entityTitleLabel;
@property (nonatomic, readonly) CALayer* firstStampLayer;
@property (nonatomic, readonly) CALayer* secondStampLayer;
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) CATextLayer* headerTextLayer;

@end

@implementation CreditTableViewCell

@synthesize stamp = stamp_;
@synthesize creditedUser = creditedUser_;
@synthesize entityTitleLabel = entityTitleLabel_;
@synthesize firstStampLayer = firstStampLayer_;
@synthesize secondStampLayer = secondStampLayer_;
@synthesize userImageView = userImageView_;
@synthesize headerTextLayer = headerTextLayer_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;

    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 41, 41)];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];

    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 12, 210, 16);
    headerTextLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                           forKey:@"contents"];
    [self.contentView.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];

    entityTitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 25, 200, 40)];
    entityTitleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24];
    entityTitleLabel_.textColor = [UIColor stampedBlackColor];
    entityTitleLabel_.highlightedTextColor = [UIColor whiteColor];
    entityTitleLabel_.backgroundColor = [UIColor clearColor];
    [self.contentView addSubview:entityTitleLabel_];
    [entityTitleLabel_ release];
    
    firstStampLayer_ = [[CALayer alloc] init];
    firstStampLayer_.frame = CGRectMake(70, 28, 18, 18);
    [self.contentView.layer addSublayer:firstStampLayer_];
    [firstStampLayer_ release];
    
    secondStampLayer_ = [[CALayer alloc] init];
    secondStampLayer_.frame = CGRectOffset(firstStampLayer_.frame, CGRectGetWidth(firstStampLayer_.frame) / 2, 0);
    [self.contentView.layer addSublayer:secondStampLayer_];
    [secondStampLayer_ release];

    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    UIImageView* disclosureArrowImageView = [[UIImageView alloc] initWithFrame:CGRectMake(290, 28, 8, 11)];
    disclosureArrowImageView.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView.image = disclosureImage;
    disclosureArrowImageView.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self.contentView addSubview:disclosureArrowImageView];
    [disclosureArrowImageView release];
  }

  return self;
}

- (void)dealloc {
  self.stamp = nil;
  self.creditedUser = nil;
  [super dealloc];
}

- (void)setStamp:(Stamp*)stamp {
  [stamp_ release];
  stamp_ = [stamp retain];
  if (stamp_) {
    NSString* title = stamp_.entityObject.title;

    userImageView_.imageURL = stamp.user.profileImageURL;

    entityTitleLabel_.text = title;
    // TODO(andybons): compositing layers. stacks.
    firstStampLayer_.contents = (id)((User*)[stamp.credits anyObject]).stampImage.CGImage;
    secondStampLayer_.contents = (id)stamp.user.stampImage.CGImage;
    
    CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24]
                                  forWidth:200
                             lineBreakMode:UILineBreakModeTailTruncation];
    CGRect stampFrame = firstStampLayer_.frame;
    stampFrame.origin.x = CGRectGetMinX(entityTitleLabel_.frame) +
        titleSize.width - 5;
    [CATransaction begin];
    [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
    firstStampLayer_.frame = stampFrame;
    CGRect secondLayerFrame = CGRectOffset(stampFrame, CGRectGetWidth(stampFrame) / 2, 0);
    secondStampLayer_.frame = secondLayerFrame;
    [CATransaction commit];
    [self.contentView setNeedsDisplay];
  }
}

- (void)setCreditedUser:(User *)creditedUser {
  [creditedUser_ release];
  creditedUser_ = [creditedUser retain];
  firstStampLayer_.contents = (id)creditedUser_.stampImage.CGImage;
}

- (void)invertColors:(BOOL)inverted {
  UIColor* color = inverted ? [UIColor whiteColor] : [UIColor stampedGrayColor];
  headerTextLayer_.string = [self headerAttributedStringWithColor:color];
  [self setNeedsDisplayInRect:headerTextLayer_.frame];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
  [super setHighlighted:highlighted animated:animated];
  [self invertColors:highlighted];
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  NSString* user = stamp_.user.screenName;
  
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* full = [NSString stringWithFormat:@"%@ gave credit for", user];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)color.CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}

@end
