//
//  ActivityTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityTableViewCell.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"

static const CGFloat kActivityBadgeSize = 21.0;

@implementation ActivityTableViewCell

@synthesize event = event_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;

    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 33, 33)];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];

    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kActivityBadgeSize + 10,
                                   CGRectGetMaxY(userImageView_.frame) - kActivityBadgeSize + 8,
                                   kActivityBadgeSize, kActivityBadgeSize);
    badgeImageView_ = [[UIImageView alloc] initWithFrame:badgeFrame];
    badgeImageView_.contentMode = UIViewContentModeCenter;
    [self.contentView addSubview:badgeImageView_];
    [badgeImageView_ release];

    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 15, 210, 16);
    headerTextLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                           forKey:@"contents"];
    [self.contentView.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];

    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithFrame:CGRectZero];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.image = disclosureImage;
    disclosureArrowImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self.contentView addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
    
    timestampLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    timestampLabel_.textColor = [UIColor stampedLightGrayColor];
    timestampLabel_.font = [UIFont fontWithName:@"Helvetica" size:10];
    timestampLabel_.highlightedTextColor = [UIColor whiteColor];
    timestampLabel_.backgroundColor = [UIColor clearColor];
    [self.contentView addSubview:timestampLabel_];
    [timestampLabel_ release];
    
    addedStampsLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 58, 200, 12)];
    addedStampsLabel_.textColor = [UIColor stampedLightGrayColor];
    addedStampsLabel_.highlightedTextColor = [UIColor whiteColor];
    addedStampsLabel_.backgroundColor = [UIColor clearColor];
    addedStampsLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
    [self.contentView addSubview:addedStampsLabel_];
    [addedStampsLabel_ release];
  }
  return self;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  disclosureArrowImageView_.frame =
      CGRectMake(290,
                 (CGRectGetHeight(self.frame) / 2) -
                     (CGRectGetHeight(disclosureArrowImageView_.frame) / 2) - 1,
                 8, 11);
  timestampLabel_.frame =
      CGRectMake(70,
                 CGRectGetHeight(self.frame) - CGRectGetHeight(timestampLabel_.frame) - 12,
                 CGRectGetWidth(timestampLabel_.frame),
                 CGRectGetHeight(timestampLabel_.frame));
  CGRect benefitFrame = timestampLabel_.frame;
  benefitFrame.size = addedStampsLabel_.frame.size;
  benefitFrame.origin.x = CGRectGetMaxX(benefitFrame) + 15;
  addedStampsLabel_.frame = benefitFrame;
}

- (void)setEvent:(Event*)event {
  if (event != event_) {
    [event_ release];
    event_ = [event retain];
  }

  if (event) {
    userImageView_.imageURL = event.user.profileImageURL;
    timestampLabel_.text = [Util userReadableTimeSinceDate:event.created];
    [timestampLabel_ sizeToFit];
    NSInteger benefit = event.benefit.integerValue;
    if (benefit > 0) {
      NSString* label = @"stamps";
      if (benefit == 1)
        label = @"stamp";
      addedStampsLabel_.text = [NSString stringWithFormat:@"+%d %@", benefit, label];
      [addedStampsLabel_ sizeToFit];
    }
    addedStampsLabel_.hidden = (benefit == 0);
  }
  [self.contentView setNeedsDisplay];
}

- (void)dealloc {
  self.event = nil;
  [super dealloc];
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
  // Stub. Should be implemented by subclasses.
  return nil;
}

@end
