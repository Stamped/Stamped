//
//  ActivityGenericTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "ActivityGenericTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "TTTAttributedLabel.h"
#import "Entity.h"
#import "Stamp.h"
#import "STImageView.h"
#import "User.h"
#import "UIColor+Stamped.h"

static const CGFloat kActivityBadgeSize = 21.0;
static const CGFloat kActivityStampSize = 16.0;

@interface ActivityGenericTableViewCell ()
@property (nonatomic, readonly) TTTAttributedLabel* subjectLabel;
@property (nonatomic, readonly) TTTAttributedLabel* blurbLabel;
@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) STImageView* iconImageView;
@property (nonatomic, readonly) STImageView* largeImageView;
@end

@implementation ActivityGenericTableViewCell

@synthesize subjectLabel = subjectLabel_;
@synthesize blurbLabel = blurbLabel_;
@synthesize stampImageView = stampImageView_;
@synthesize iconImageView = iconImageView_;
@synthesize largeImageView = largeImageView_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    userImageView_.hidden = YES;

    largeImageView_ = [[STImageView alloc] initWithFrame:CGRectMake(15, 10, 41, 41)];
    largeImageView_.backgroundColor = [UIColor clearColor];
    largeImageView_.layer.shadowOpacity = 0;
    [self.contentView addSubview:largeImageView_];
    largeImageView_.hidden = YES;
    [largeImageView_ release];
    
    CGRect stampFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - (kActivityStampSize / 2),
                                   CGRectGetMinY(userImageView_.frame) - (kActivityStampSize / 2),
                                   kActivityStampSize, kActivityStampSize);
    stampImageView_ = [[UIImageView alloc] initWithFrame:stampFrame];
    stampImageView_.hidden = YES;
    [self.contentView addSubview:stampImageView_];
    [stampImageView_ release];
    
    CGRect iconFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kActivityBadgeSize + 10,
                                  CGRectGetMaxY(userImageView_.frame) - kActivityBadgeSize + 8,
                                  kActivityBadgeSize, kActivityBadgeSize);
    iconImageView_ = [[STImageView alloc] initWithFrame:iconFrame];
    iconImageView_.backgroundColor = [UIColor clearColor];
    iconImageView_.layer.shadowOpacity = 0;
    iconImageView_.hidden = YES;
    [self.contentView addSubview:iconImageView_];
    [iconImageView_ release];
    
    subjectLabel_ = [[TTTAttributedLabel alloc] initWithFrame:CGRectMake(70, 29, 210, 20)];
    subjectLabel_.numberOfLines = 0;
    subjectLabel_.backgroundColor = [UIColor clearColor];
    subjectLabel_.textColor = [UIColor stampedGrayColor];
    subjectLabel_.highlightedTextColor = [UIColor whiteColor];
    subjectLabel_.lineBreakMode = UILineBreakModeWordWrap;
    subjectLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    subjectLabel_.hidden = YES;
    [self.contentView addSubview:subjectLabel_];
    [subjectLabel_ release];
    
    blurbLabel_ = [[TTTAttributedLabel alloc] initWithFrame:CGRectMake(70, 29, 210, 20)];
    blurbLabel_.numberOfLines = 0;
    blurbLabel_.backgroundColor = [UIColor clearColor];
    blurbLabel_.textColor = [UIColor stampedBlackColor];
    blurbLabel_.highlightedTextColor = [UIColor whiteColor];
    blurbLabel_.lineBreakMode = UILineBreakModeWordWrap;
    blurbLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    blurbLabel_.hidden = YES;
    [self.contentView addSubview:blurbLabel_];
    [blurbLabel_ release];
  }
  return self;
}

- (void)dealloc {
  subjectLabel_ = nil;
  blurbLabel_ = nil;
  stampImageView_ = nil;
  iconImageView_ = nil;
  largeImageView_ = nil;
  [super dealloc];
}

- (void)prepareForReuse {
  subjectLabel_.hidden = YES;
  subjectLabel_.text = nil;
  blurbLabel_.hidden = YES;
  blurbLabel_.text = nil;
  stampImageView_.hidden = YES;
  iconImageView_.hidden = YES;
  largeImageView_.hidden = YES;
  userImageView_.frame = CGRectMake(15, 10, 33, 33);
  userImageView_.hidden = YES;
  disclosureArrowImageView_.hidden = NO;
  [super prepareForReuse];
  self.selectionStyle = UITableViewCellSelectionStyleBlue;
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
  
  if (!event.stamp && !event.entityObject && !event.user && !event.URL) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    disclosureArrowImageView_.hidden = YES;
  }
  
  if ([event.icon isEqualToString:@"stamp"]) {
    stampImageView_.image = [event.user stampImageWithSize:StampImageSize16];
    stampImageView_.hidden = NO;
    userImageView_.hidden = NO;
  } else if (event.icon) {
    iconImageView_.imageURL = event.icon;
    iconImageView_.hidden = NO;
    userImageView_.hidden = NO;
  } else if (!event.icon && event.image) {
    if ([event.image isEqualToString:@"user"]) {
      userImageView_.frame = CGRectMake(15, 10, 41, 41);
      userImageView_.hidden = NO;
    } else {
      largeImageView_.imageURL = event.image;
      largeImageView_.hidden = NO;
    }
  }

  if (!userImageView_.hidden)
    userImageView_.imageURL = [event.user profileImageURLForSize:ProfileImageSize37];

  if (event.subject) {
    subjectLabel_.text = event.subject;
    CGSize stringSize = [event.subject sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]
                                  constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                      lineBreakMode:UILineBreakModeWordWrap];
    CGRect textFrame = subjectLabel_.frame;
    textFrame.origin.y = 12;
    textFrame.size = stringSize;
    subjectLabel_.frame = textFrame;
    subjectLabel_.hidden = NO;
  }
  
  if (event.blurb) {
    blurbLabel_.text = event.blurb;
    CGSize stringSize = [event.blurb sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]
                                constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                    lineBreakMode:UILineBreakModeWordWrap];
    CGRect textFrame = blurbLabel_.frame;
    if (subjectLabel_.text) {
      textFrame.origin.y = CGRectGetMaxY(subjectLabel_.frame) + 2;
    } else {
      textFrame.origin.y = 12;
    }
    textFrame.size = stringSize;
    blurbLabel_.frame = textFrame;
    blurbLabel_.hidden = NO;
  }
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  return nil;
}


@end
