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

@end

@implementation ActivityCreditTableViewCell

@synthesize entityTitleLabel = entityTitleLabel_;
@synthesize firstStampLayer = firstStampLayer_;
@synthesize secondStampLayer = secondStampLayer_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    userImageView_.frame = CGRectMake(15, 10, 41, 41);

    badgeImageView_.hidden = YES;
    
    headerTextLayer_.frame = CGRectOffset(headerTextLayer_.frame, 0, -3);

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
  }
  return self;
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
  if (!event)
    return;

  userImageView_.imageURL = [event.user profileImageURLForSize:ProfileImageSize37];
  NSString* title = event.stamp.entityObject.title;
  entityTitleLabel_.text = title;
  User* currentUser = [[AccountManager sharedManager] currentUser];
  firstStampLayer_.contents = (id)[currentUser stampImageWithSize:StampImageSize12].CGImage;
  secondStampLayer_.contents = (id)[event.user stampImageWithSize:StampImageSize12].CGImage;
  

  CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24]
                                forWidth:200
                           lineBreakMode:UILineBreakModeTailTruncation];
  CGRect stampFrame = firstStampLayer_.frame;
  stampFrame.origin.x = CGRectGetMinX(entityTitleLabel_.frame) + titleSize.width - 5;
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  firstStampLayer_.frame = stampFrame;
  CGRect secondLayerFrame = CGRectOffset(stampFrame, CGRectGetWidth(stampFrame) / 2, 0);
  secondStampLayer_.frame = secondLayerFrame;
  [CATransaction commit];
  [self.contentView setNeedsDisplay];
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
