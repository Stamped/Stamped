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
  subjectLabel_.text = nil;
  blurbLabel_.text = nil;
  stampImageView_.hidden = YES;
  iconImageView_.hidden = YES;
  largeImageView_.hidden = YES;
  userImageView_.frame = CGRectMake(15, 10, 33, 33);
  userImageView_.hidden = YES;
  [super prepareForReuse];
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
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

  NSLog(@"Image: %@", event.image);
  NSLog(@"Icon: %@\n--", event.icon);
  
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  return nil;
}


@end
