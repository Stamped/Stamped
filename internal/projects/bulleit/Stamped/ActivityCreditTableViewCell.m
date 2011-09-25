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
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"

@interface ActivityCreditTableViewCell ()

@property (nonatomic, readonly) UILabel* entityTitleLabel;
@property (nonatomic, readonly) CALayer* firstStampLayer;
@property (nonatomic, readonly) CALayer* secondStampLayer;
@property (nonatomic, readonly) UILabel* plusStampsLabel;

@end

@implementation ActivityCreditTableViewCell

@synthesize entityTitleLabel = entityTitleLabel_;
@synthesize firstStampLayer = firstStampLayer_;
@synthesize secondStampLayer = secondStampLayer_;
@synthesize plusStampsLabel = plusStampsLabel_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    userImageView_.frame = CGRectMake(15, 10, 41, 41);

    entityTitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 25, 200, 40)];
    entityTitleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
    entityTitleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
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
    
    plusStampsLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 58, 200, 12)];
    plusStampsLabel_.textColor = [UIColor stampedLightGrayColor];
    plusStampsLabel_.highlightedTextColor = [UIColor whiteColor];
    plusStampsLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
    [self.contentView addSubview:plusStampsLabel_];
    [plusStampsLabel_ release];
  }
  return self;
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
  if (!event)
    return;

  userImageView_.imageURL = event.user.profileImageURL;
  headerTextLayer_.string = [self headerAttributedStringWithColor:[UIColor stampedGrayColor]];
  NSString* title = event.stamp.entityObject.title;
  entityTitleLabel_.text = title;
  User* currentUser = [[AccountManager sharedManager] currentUser];
  firstStampLayer_.contents = (id)currentUser.stampImage.CGImage;
  secondStampLayer_.contents = (id)event.user.stampImage.CGImage;
  plusStampsLabel_.text = [NSString stringWithFormat:@"+%d stamps", event.benefit.integerValue];

  CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27]
                                forWidth:200
                           lineBreakMode:UILineBreakModeTailTruncation];
  CGRect stampFrame = firstStampLayer_.frame;
  stampFrame.origin.x = CGRectGetMinX(headerTextLayer_.frame) +
      titleSize.width - (CGRectGetWidth(stampFrame) / 2);
  CGRect oldFrame = firstStampLayer_.frame;
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  firstStampLayer_.frame = stampFrame;
  [self.contentView setNeedsDisplayInRect:oldFrame];
  [self.contentView setNeedsDisplayInRect:stampFrame];
  oldFrame = secondStampLayer_.frame;
  CGRect secondLayerFrame = CGRectOffset(stampFrame, CGRectGetWidth(stampFrame) / 2, 0);
  secondStampLayer_.frame = secondLayerFrame;
  [CATransaction commit];
  [self.contentView setNeedsDisplayInRect:oldFrame];
  [self.contentView setNeedsDisplayInRect:secondLayerFrame];
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* user = self.event.user.screenName;
  NSString* full = [NSString stringWithFormat:@"%@ %@", user, @"gave you credit for"];
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
