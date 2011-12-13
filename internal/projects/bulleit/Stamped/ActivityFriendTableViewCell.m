//
//  ActivityFriendTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityFriendTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "TTTAttributedLabel.h"
#import "User.h"
#import "UIColor+Stamped.h"

static const CGFloat kActivityStampSize = 14.0;

@interface ActivityFriendTableViewCell ()
@property (nonatomic, readonly) TTTAttributedLabel* textLabel;
@property (nonatomic, readonly) UIImageView* stampImageView;
@end

@implementation ActivityFriendTableViewCell

@synthesize textLabel = textLabel_;
@synthesize stampImageView = stampImageView_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    textLabel_ = [[TTTAttributedLabel alloc] initWithFrame:CGRectMake(70, 29, 210, 20)];
    textLabel_.numberOfLines = 0;
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor stampedGrayColor];
    textLabel_.highlightedTextColor = [UIColor whiteColor];
    textLabel_.lineBreakMode = UILineBreakModeWordWrap;
    textLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self.contentView addSubview:textLabel_];
    [textLabel_ release];
    
    CGRect stampFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - (kActivityStampSize / 2),
                                   CGRectGetMinY(userImageView_.frame) - (kActivityStampSize / 2),
                                   kActivityStampSize, kActivityStampSize);
    stampImageView_ = [[UIImageView alloc] initWithFrame:stampFrame];
    [self.contentView addSubview:stampImageView_];
    [stampImageView_ release];
  }
  return self;
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  return nil;
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
  if (!event)
    return;

  NSString* full = [NSString stringWithFormat:@"%@ just joined Stamped as %@",
      self.event.subject, self.event.user.screenName];

  [textLabel_ setText:full afterInheritingLabelAttributesAndConfiguringWithBlock:^(NSMutableAttributedString* mutableAttributedString) {
    NSRange boldRange = [[mutableAttributedString string] rangeOfString:self.event.user.screenName
                                                                options:NSBackwardsSearch];
    CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
    if (font) {
      [mutableAttributedString addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:boldRange];
      CFRelease(font);
    }
    return mutableAttributedString;
  }];

  CGSize stringSize = [full sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]
                       constrainedToSize:CGSizeMake(210, MAXFLOAT)
                           lineBreakMode:UILineBreakModeWordWrap];
  CGRect textFrame = textLabel_.frame;
  textFrame.origin.y = 14;
  textFrame.size = stringSize;
  textLabel_.frame = textFrame;
  
  stampImageView_.image = [event.user stampImageWithSize:StampImageSize14];
  [self.contentView setNeedsDisplay];
}

@end
