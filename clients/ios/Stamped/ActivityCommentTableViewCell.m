//
//  ActivityCommentTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityCommentTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"

@interface ActivityCommentTableViewCell ()

@property (nonatomic, readonly) UILabel* textLabel;
@end

@implementation ActivityCommentTableViewCell

@synthesize textLabel = textLabel_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(69, 29, 210, 20)];
    textLabel_.numberOfLines = 0;
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor colorWithWhite:0.15 alpha:1.0];
    textLabel_.highlightedTextColor = [UIColor whiteColor];
    textLabel_.lineBreakMode = UILineBreakModeWordWrap;
    textLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self.contentView addSubview:textLabel_];
    [textLabel_ release];
  }
  return self;
}

- (void)setEvent:(Event*)event {
  [super setEvent:event];
  if (!event)
    return;

  if ([event.genre isEqualToString:@"mention"]) {
    badgeImageView_.image = [UIImage imageNamed:@"activity_mention_badge"];
  } else {
    badgeImageView_.image = [UIImage imageNamed:@"activity_comment_badge"];
  }
  
  textLabel_.text = event.blurb;
  CGSize stringSize = [event.blurb sizeWithFont:textLabel_.font
                              constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                  lineBreakMode:UILineBreakModeWordWrap];
  CGRect textFrame = textLabel_.frame;
  textFrame.size = stringSize;
  textLabel_.frame = textFrame;
  [self.contentView setNeedsDisplay];
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  NSString* user = self.event.user.screenName;

  NSString* actionString = @"";
  if ([self.event.genre isEqualToString:@"reply"]) {
    actionString = @"replied on";
  } else if ([self.event.genre isEqualToString:@"comment"]) {
    actionString = @"commented on";
  } else if ([self.event.genre isEqualToString:@"mention"]) {
    actionString = @"mentioned you on";
  }

  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* entityTitle = self.event.stamp.entityObject.title;
  NSString* full = [NSString stringWithFormat:@"%@ %@ %@", user, actionString, entityTitle];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)color.CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:[full rangeOfString:entityTitle]];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}

@end
