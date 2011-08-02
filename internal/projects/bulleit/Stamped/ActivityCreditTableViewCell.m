//
//  ActivityCreditTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityCreditTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Event.h"
#import "Stamp.h"
#import "User.h"
#import "UserImageView.h"
#import "Util.h"

@interface ActivityCreditCellView : UIView
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;

@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UIImageView* disclosureArrowImageView;
@property (nonatomic, readonly) CATextLayer* headerTextLayer;
@property (nonatomic, readonly) UILabel* entityTitleLabel;
@property (nonatomic, readonly) CALayer* firstStampLayer;
@property (nonatomic, readonly) CALayer* secondStampLayer;
@end

@implementation ActivityCreditCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize userImageView = userImageView_;
@synthesize headerTextLayer = headerTextLayer_;
@synthesize entityTitleLabel = entityTitleLabel_;
@synthesize firstStampLayer = firstStampLayer_;
@synthesize secondStampLayer = secondStampLayer_;
@synthesize disclosureArrowImageView = disclosureArrowImageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.autoresizingMask = (UIViewAutoresizingFlexibleWidth |
                             UIViewAutoresizingFlexibleHeight);
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 41, 41)];
    [self addSubview:userImageView_];
    [userImageView_ release];

    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor colorWithWhite:0.6 alpha:1.0].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 13, 220, 16);
    NSDictionary* actions = [[NSDictionary alloc] initWithObjectsAndKeys:[NSNull null], @"contents", nil];
    headerTextLayer_.actions = actions;
    [actions release];
    [self.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];
    
    entityTitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 25, 220, 40)];
    entityTitleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
    entityTitleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
    entityTitleLabel_.highlightedTextColor = [UIColor whiteColor];
    entityTitleLabel_.backgroundColor = [UIColor clearColor];
    [self addSubview:entityTitleLabel_];
    [entityTitleLabel_ release];
    
    firstStampLayer_ = [[CALayer alloc] init];
    firstStampLayer_.frame = CGRectMake(70, 28, 18, 18);
    [self.layer addSublayer:firstStampLayer_];
    [firstStampLayer_ release];
    
    secondStampLayer_ = [[CALayer alloc] init];
    secondStampLayer_.frame = CGRectOffset(firstStampLayer_.frame, CGRectGetWidth(firstStampLayer_.frame) / 2, 0);
    [self.layer addSublayer:secondStampLayer_];
    [secondStampLayer_ release];
    
    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(290, 26, 8, 11)];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.image = disclosureImage;
    disclosureArrowImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
  }
  return self;
}

- (void)invertColors:(BOOL)inverted {
  NSMutableAttributedString* headerAttributedString =
      [[NSMutableAttributedString alloc] initWithAttributedString:headerTextLayer_.string];
  CGColorRef color = inverted ? [UIColor whiteColor].CGColor :
                                [UIColor colorWithWhite:0.6 alpha:1.0].CGColor;
  [headerAttributedString setAttributes:
      [NSDictionary dictionaryWithObject:(id)color 
                                  forKey:(id)kCTForegroundColorAttributeName] 
                                  range:NSMakeRange(0, headerAttributedString.length)];
  headerTextLayer_.string = headerAttributedString;
  [headerAttributedString release];
  [self setNeedsDisplayInRect:headerTextLayer_.frame];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  selected_ = selected;
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted {
  highlighted_ = highlighted;
  [self invertColors:highlighted];
}

@end

@implementation ActivityCreditTableViewCell

@synthesize event = event_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0, 0, self.contentView.bounds.size.width,
                                        self.contentView.bounds.size.height);
		customView_ = [[ActivityCreditCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
}

- (void)setEvent:(Event*)event {
  if (event == event_)
    return;
  
  [event_ release];
  event_ = [event retain];
  if (!event)
    return;

  customView_.userImageView.image = event.user.profileImage;
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* user = event.user.displayName;
  NSString* full = [NSString stringWithFormat:@"%@ %@", user, @"gave you credit for"];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)[UIColor colorWithWhite:0.6 alpha:1.0].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  CFRelease(font);
  CFRelease(style);
  customView_.headerTextLayer.string = string;
  NSString* title = event.stamp.entityObject.title;
  customView_.entityTitleLabel.text = title;
  User* currentUser = [[AccountManager sharedManager] currentUser];
  customView_.firstStampLayer.contents = (id)currentUser.stampImage.CGImage;
  customView_.secondStampLayer.contents = (id)event.user.stampImage.CGImage;

  CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27]
                                forWidth:220
                           lineBreakMode:UILineBreakModeTailTruncation];
  CGRect stampFrame = customView_.firstStampLayer.frame;
  stampFrame.origin.x = CGRectGetMinX(customView_.headerTextLayer.frame) +
      titleSize.width - (CGRectGetWidth(stampFrame) / 2);
  CGRect oldFrame = customView_.firstStampLayer.frame;
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  customView_.firstStampLayer.frame = stampFrame;
  [customView_ setNeedsDisplayInRect:oldFrame];
  [customView_ setNeedsDisplayInRect:stampFrame];
  oldFrame = customView_.secondStampLayer.frame;
  CGRect secondLayerFrame = CGRectOffset(stampFrame, CGRectGetWidth(stampFrame) / 2, 0);
  customView_.secondStampLayer.frame = secondLayerFrame;
  [CATransaction commit];
  [customView_ setNeedsDisplayInRect:oldFrame];
  [customView_ setNeedsDisplayInRect:secondLayerFrame];
}
@end
